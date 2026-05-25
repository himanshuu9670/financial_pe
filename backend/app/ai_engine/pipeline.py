"""
Transaction extraction pipeline:
PDF spans → bank detection → columns → rows → transactions → validation
"""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from app.ai_engine.bank_classifier import classify_bank
from app.ai_engine.models import ParseDebugInfo, TransactionParseResult
from app.shared.models import StructuredTransaction, TransactionSummary
from app.ai_engine.span_utils import flatten_spans
from app.ai_engine.transaction_detector import detect_transactions_on_page
from app.pdf_engine.models import DocumentExtraction
from app.utils.logging import get_logger

logger = get_logger(__name__)


def run_transaction_pipeline(
    document: DocumentExtraction,
    *,
    include_debug: bool = False,
) -> TransactionParseResult:
    bank_info = classify_bank(document)
    spans = flatten_spans(document)

    by_page: dict[int, list] = defaultdict(list)
    page_widths: dict[int, float] = {}
    for ps in spans:
        by_page[ps.page].append(ps)
        page_widths[ps.page] = ps.page_width

    all_transactions: list[StructuredTransaction] = []
    all_columns = []
    all_rows = []
    global_idx = 0

    for page_num in sorted(by_page.keys()):
        page_spans = by_page[page_num]
        txns, columns, rows = detect_transactions_on_page(
            page_spans,
            page_widths.get(page_num, 595),
            global_idx,
        )
        all_transactions.extend(txns)
        global_idx += len(txns)
        if include_debug:
            all_columns.extend(columns)
            all_rows.extend(rows)

    from app.financial_engine.validator import validate_transactions

    summary, validation_issues = validate_transactions(all_transactions)
    warnings: list[str] = list(validation_issues)

    if document.is_likely_scanned:
        warnings.append("Document appears scanned — transaction detection may be incomplete.")

    if bank_info.bank == "UNKNOWN":
        warnings.append("Bank could not be identified — using generic column detection.")

    debug = None
    if include_debug:
        header_idx = next((r.row_index for r in all_rows if r.is_header), None)
        debug = ParseDebugInfo(
            columns=all_columns[:20],
            grouped_row_count=len(all_rows),
            raw_row_count=len(all_rows),
            header_row_index=header_idx,
        )

    logger.info(
        "transaction_pipeline_complete",
        bank=bank_info.bank,
        count=len(all_transactions),
        confidence=bank_info.confidence,
    )

    return TransactionParseResult(
        bank=bank_info.bank,
        bank_confidence=bank_info.confidence,
        transactions=all_transactions,
        summary=summary,
        debug=debug,
        warnings=warnings,
    )

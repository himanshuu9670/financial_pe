"""Phase 9 AI intelligence unit tests."""

from decimal import Decimal

from app.shared.models import StructuredTransaction, TransactionSummary
from app.ai_engine.models import TransactionParseResult
from app.ai_intelligence.anomaly_detector import detect_anomalies
from app.ai_intelligence.categorizer import categorize_transactions
from app.ai_intelligence.pipeline import run_ai_pipeline
from app.ai_intelligence.semantic_parser import parse_semantic
from app.ai_intelligence.smart_corrector import suggest_corrections
from app.ai_intelligence.embeddings_cache import (
    build_cache_payload,
    load_index_from_meta,
    transactions_fingerprint,
)
from app.ai_intelligence.embeddings_engine import EmbeddingsIndex


def _txn(desc: str, debit=None, credit=None, balance=None, row=0) -> StructuredTransaction:
    return StructuredTransaction(
        page=1,
        row_index=row,
        description=desc,
        debit=Decimal(str(debit)) if debit is not None else None,
        credit=Decimal(str(credit)) if credit is not None else None,
        balance=Decimal(str(balance)) if balance is not None else None,
    )


def test_semantic_parser_travel():
    sem = parse_semantic("IRCTC WEB PAYMENT")
    assert sem["category_hint"] == "Travel"
    assert sem["category_confidence"] > 0.4


def test_categorizer_food():
    txns = [_txn("SWIGGY PAYMENT", debit=450)]
    cats = categorize_transactions(txns)
    assert cats[0].category == "Food"
    assert cats[0].confidence >= 0.45


def test_ocr_correction():
    from app.ai_intelligence.smart_corrector import _fix_amount_string

    fixed, conf = _fix_amount_string("5O00.OO")
    assert fixed == "5000.00"
    assert conf >= 0.8

    txns = [
        StructuredTransaction(
            page=1,
            row_index=0,
            description="ATM",
            debit=Decimal("5000.00"),
        )
    ]
    fixes = suggest_corrections(txns)
    assert isinstance(fixes, list)


def test_anomaly_large_debit():
    txns = [_txn("ATM WDL", debit=600_000, balance=100)]
    flags = detect_anomalies(txns)
    assert any(f.anomaly_type == "large_withdrawal" for f in flags)


def test_embeddings_cache_fingerprint_stable():
    txns = [_txn("SWIGGY", debit=100), _txn("AMAZON", debit=200)]
    fp1 = transactions_fingerprint(txns)
    fp2 = transactions_fingerprint(txns)
    assert fp1 == fp2


def test_embeddings_cache_reuse():
    txns = [_txn("IRCTC WEB", debit=500)]
    meta = {}
    idx1, frag1, hit1 = load_index_from_meta(meta, txns)
    assert hit1 is False
    meta.update(frag1)
    idx2, _, hit2 = load_index_from_meta(meta, txns)
    assert hit2 is True
    assert len(idx1.entries) == len(idx2.entries)


def test_semantic_search_travel_query():
    txns = [
        _txn("IRCTC TICKET", debit=1200),
        _txn("SWIGGY FOOD", debit=300),
    ]
    index = EmbeddingsIndex(txns)
    hits = index.semantic_search("travel railway", limit=5)
    assert hits
    assert hits[0][0] == txns[0].transaction_id


def test_pipeline_full():
    txns = [
        _txn("SWIGGY", debit=200, balance=9800, row=0),
        _txn("IRCTC", debit=1500, balance=8300, row=1),
        _txn("SALARY CREDIT", credit=50000, balance=58300, row=2),
    ]
    parse = TransactionParseResult(
        bank="hdfc",
        bank_confidence=0.9,
        transactions=txns,
        summary=TransactionSummary(validation_passed=True, transaction_count=3),
    )
    report = run_ai_pipeline("test-id", txns, parse, ocr_confidence=0.8, layout_confidence=0.85)
    assert len(report.categories) == 3
    assert report.confidence.overall > 0.5
    assert report.fraud.risk_level in ("low", "medium", "high", "critical")

"""
PDF export pipeline — apply invisible edits and write to storage/edited_pdfs.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import UUID

from app.pdf_engine.edit_models import ExportResult, TargetSpan, VisualValidationMetrics
from app.pdf_engine.editor import collect_targets_from_ledger
from app.pdf_engine.exceptions import PdfEngineError
from app.pdf_engine.text_replacer import replace_in_pdf
from app.pdf_engine.visual_validator import validate_export
from app.financial_engine.models import LedgerEntry
from app.utils.logging import get_logger

logger = get_logger(__name__)


class PdfExportEngine:
    def export(
        self,
        statement_id: UUID,
        source_pdf: Path,
        output_pdf: Path,
        entries: list[LedgerEntry],
        *,
        extraction_json: dict | None = None,
        is_likely_scanned: bool = False,
    ) -> ExportResult:
        warnings: list[str] = []

        if is_likely_scanned:
            warnings.append(
                "Document may be scanned — OCR overlay editing recommended (future phase)."
            )

        page_width = 595.0
        if extraction_json and extraction_json.get("pages"):
            page_width = float(extraction_json["pages"][0].get("width", 595))

        targets = collect_targets_from_ledger(entries, page_width=page_width)

        if not targets:
            shutil.copy2(source_pdf, output_pdf)
            return ExportResult(
                output_path=str(output_pdf),
                replacements_applied=0,
                replacements_failed=0,
                validation=VisualValidationMetrics(passed=True, regions_checked=0),
                warnings=["No coordinate-backed changes to apply — original copied."],
                is_scanned_fallback_recommended=is_likely_scanned,
            )

        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        results = replace_in_pdf(source_pdf, output_pdf, targets)

        applied = sum(1 for r in results if r.applied)
        failed = len(results) - applied

        validation = validate_export(source_pdf, output_pdf, targets)
        if failed:
            warnings.append(f"{failed} replacement(s) failed")

        logger.info(
            "pdf_export_complete",
            statement_id=str(statement_id),
            applied=applied,
            failed=failed,
            validation_passed=validation.passed,
        )

        return ExportResult(
            output_path=str(output_pdf),
            replacements_applied=applied,
            replacements_failed=failed,
            validation=validation,
            warnings=warnings,
            is_scanned_fallback_recommended=is_likely_scanned,
        )

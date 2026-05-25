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
    def _validate_targets(self, entries: list[LedgerEntry], targets: list[TargetSpan]) -> list[str]:
        issues: list[str] = []
        seen: set[tuple[str, int, str, int, tuple[float, ...]]] = set()

        for target in targets:
            if target.row_index is None:
                issues.append(
                    f"transaction_overlay_mismatch: missing row_index for target {target.transaction_id}:{target.field}"
                )
                logger.warning(
                    "transaction_overlay_mismatch",
                    transaction_id=target.transaction_id,
                    field=target.field,
                    page=target.page,
                    bbox=target.bbox,
                )

            key = (
                target.transaction_id,
                target.row_index,
                target.field,
                target.page,
                tuple(target.bbox),
            )
            if key in seen:
                issues.append(
                    f"duplicate_overlay_target: {target.transaction_id}:{target.field} page={target.page} row={target.row_index}"
                )
                logger.warning(
                    "duplicate_overlay_target",
                    transaction_id=target.transaction_id,
                    field=target.field,
                    page=target.page,
                    row_index=target.row_index,
                    bbox=target.bbox,
                )
            else:
                seen.add(key)

        # Validate every changed field has a unique overlay target.
        for entry in entries:
            for field in ("debit", "credit", "balance"):
                current = getattr(entry, field)
                original = getattr(entry, f"original_{field}")
                if current is None:
                    continue
                if original is not None and current == original:
                    continue
                coord = getattr(entry.coordinates, field, None)
                if not coord or not coord.bbox or len(coord.bbox) < 4:
                    issues.append(
                        f"transaction_overlay_mismatch: missing coordinate for edited {field} on {entry.transaction_id}"
                    )
                    logger.warning(
                        "transaction_overlay_mismatch",
                        transaction_id=entry.transaction_id,
                        field=field,
                        row_index=entry.row_index,
                        page=entry.page,
                    )
                    continue

                matched = [
                    t
                    for t in targets
                    if t.transaction_id == entry.transaction_id
                    and t.row_index == entry.row_index
                    and t.field == field
                ]
                if len(matched) == 0:
                    issues.append(
                        f"transaction_overlay_mismatch: no target for edited {field} on {entry.transaction_id}"
                    )
                    logger.warning(
                        "transaction_overlay_mismatch",
                        transaction_id=entry.transaction_id,
                        field=field,
                        row_index=entry.row_index,
                        page=entry.page,
                    )
                elif len(matched) > 1:
                    issues.append(
                        f"duplicate_overlay_target: multiple targets for {entry.transaction_id}:{field}"
                    )
                    logger.warning(
                        "duplicate_overlay_target",
                        transaction_id=entry.transaction_id,
                        field=field,
                        row_index=entry.row_index,
                        page=entry.page,
                        count=len(matched),
                    )

        # Ensure downstream balances are fully mapped if any transaction edit exists.
        edited_rows = [
            entry.row_index
            for entry in entries
            if any(
                getattr(entry, field) is not None
                and (getattr(entry, f"original_{field}") is None
                     or getattr(entry, field) != getattr(entry, f"original_{field}"))
                for field in ("debit", "credit", "balance")
            )
        ]
        if edited_rows:
            min_row = min(edited_rows)
            balance_coords = [
                entry
                for entry in entries
                if entry.row_index >= min_row
                and entry.coordinates.balance
                and entry.coordinates.balance.bbox
                and len(entry.coordinates.balance.bbox) >= 4
            ]
            balance_targets = [t for t in targets if t.field == "balance"]
            if len(balance_targets) < len(balance_coords):
                issues.append(
                    f"missing_balance_target: expected {len(balance_coords)} balance targets, found {len(balance_targets)}"
                )
                logger.warning(
                    "missing_balance_target",
                    expected=len(balance_coords),
                    found=len(balance_targets),
                    start_row=min_row,
                )

        return issues

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

        validation_issues = self._validate_targets(entries, targets)
        if validation_issues:
            logger.warning(
                "pdf_export_target_validation_failed",
                statement_id=str(statement_id),
                issues=validation_issues,
            )
            raise PdfEngineError(
                "Overlay target validation failed: " + "; ".join(validation_issues)
            )

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

"""
Post-export visual validation — text and bbox consistency in edited regions.
"""

from __future__ import annotations

from pathlib import Path

import fitz

from app.pdf_engine.edit_models import TargetSpan, VisualValidationMetrics
from app.pdf_engine.pdf_loader import open_pdf


def validate_export(
    original_path: Path,
    edited_path: Path,
    targets: list[TargetSpan],
) -> VisualValidationMetrics:
    issues: list[str] = []
    checked = 0
    matches = 0
    overlap_sum = 0.0

    if not edited_path.exists():
        return VisualValidationMetrics(
            passed=False,
            issues=["Edited PDF not found"],
        )

    try:
        doc = open_pdf(edited_path)
    except Exception as exc:
        return VisualValidationMetrics(passed=False, issues=[str(exc)])

    try:
        for span in targets:
            page_index = span.page - 1
            if page_index < 0 or page_index >= doc.page_count:
                issues.append(f"Page {span.page} out of range")
                continue

            page = doc[page_index]
            rect = fitz.Rect(span.bbox)
            text_in_region = page.get_textbox(rect).strip().replace("\n", " ")
            checked += 1

            new_clean = span.new_text.replace(",", "").replace(" ", "")
            region_clean = text_in_region.replace(",", "").replace(" ", "")

            if new_clean and new_clean in region_clean or region_clean.endswith(new_clean):
                matches += 1
                overlap_sum += 1.0
            elif new_clean and region_clean:
                overlap_sum += 0.5
                issues.append(
                    f"Row {span.transaction_id[:8]} {span.field}: "
                    f"expected '{span.new_text}', found '{text_in_region[:40]}'"
                )
            elif not region_clean and span.new_text:
                issues.append(f"Empty region after edit for {span.field}")

        text_ratio = matches / checked if checked else 1.0
        bbox_ratio = overlap_sum / checked if checked else 1.0
        passed = text_ratio >= 0.85 and len(issues) <= max(1, checked // 4)

        return VisualValidationMetrics(
            text_match_ratio=round(text_ratio, 3),
            bbox_overlap_ratio=round(bbox_ratio, 3),
            regions_checked=checked,
            issues=issues[:20],
            passed=passed,
        )
    finally:
        doc.close()

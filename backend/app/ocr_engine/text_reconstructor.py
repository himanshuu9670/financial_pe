"""Parse Tesseract dict output into normalized word records."""

from __future__ import annotations

from typing import Any


def tesseract_dict_to_words(data: dict[str, Any], scale: float = 1.0) -> list[dict]:
    words: list[dict] = []
    n = len(data.get("text", []))
    for i in range(n):
        text = (data["text"][i] or "").strip()
        if not text:
            continue
        try:
            conf = int(data["conf"][i])
        except (ValueError, TypeError):
            conf = -1
        if conf < 0:
            continue

        x = float(data["left"][i]) / scale
        y = float(data["top"][i]) / scale
        w = float(data["width"][i]) / scale
        h = float(data["height"][i]) / scale
        words.append(
            {
                "text": text,
                "x": round(x, 2),
                "y": round(y, 2),
                "width": round(w, 2),
                "height": round(h, 2),
                "bbox": [round(x, 2), round(y, 2), round(x + w, 2), round(y + h, 2)],
                "conf": conf,
            }
        )
    return words

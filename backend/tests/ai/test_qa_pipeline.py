"""AI intelligence QA — categorization and anomaly smoke."""

from decimal import Decimal

from app.shared.models import StructuredTransaction
from app.ai_intelligence.anomaly_detector import detect_anomalies
from app.ai_intelligence.categorizer import categorize_transactions
from app.ai_intelligence.semantic_parser import parse_semantic


def _txn(desc: str, debit=None, row=0) -> StructuredTransaction:
    return StructuredTransaction(
        page=1,
        row_index=row,
        description=desc,
        debit=Decimal(str(debit)) if debit is not None else None,
    )


def test_semantic_parser_returns_category():
    sem = parse_semantic("SWIGGY FOOD ORDER BANGALORE")
    assert sem["category_hint"]
    assert 0 <= sem["category_confidence"] <= 1


def test_categorizer_returns_category():
    cats = categorize_transactions([_txn("SWIGGY PAYMENT", debit=450)])
    assert cats[0].category
    assert 0 <= cats[0].confidence <= 1


def test_anomaly_detector_empty_safe():
    assert detect_anomalies([]) == []


def test_anomaly_flags_outlier_debit():
    txns = [_txn("NORMAL", debit=100, row=i) for i in range(20)]
    txns.append(_txn("SPIKE", debit=50000, row=21))
    flags = detect_anomalies(txns)
    assert len(flags) >= 1

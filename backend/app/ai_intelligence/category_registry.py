"""Extensible category registry — keyword families, not hardcoded per-bank layouts."""

from __future__ import annotations

CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("Food", ["swiggy", "zomato", "restaurant", "cafe", "food", "pizza", "burger", "dominos", "eat"]),
    ("Travel", ["irctc", "uber", "ola", "makemytrip", "flight", "railway", "metro", "travel", "hotel", "booking"]),
    ("ATM", ["atm", "cash wdl", "cash withdrawal", "nfs/cash", "atm wdl"]),
    ("UPI", ["upi", "paytm", "phonepe", "gpay", "google pay", "bhim", "vpa", "ybl", "axl"]),
    ("Salary", ["salary", "payroll", "neft salary", "credited salary", "wages"]),
    ("Shopping", ["amazon", "flipkart", "myntra", "mall", "retail", "shopping", "store"]),
    ("Transfer", ["neft", "imps", "rtgs", "transfer", "sent to", "received from", "fund trf"]),
    ("Recharge", ["recharge", "jio", "airtel", "vi mobile", "prepaid", "postpaid"]),
    ("Utilities", ["electricity", "water bill", "gas", "broadband", "utility", "bescom", "mseb"]),
    ("EMI", ["emi", "loan emi", "installment", "hdfc loan", "auto debit emi"]),
    ("Loans", ["loan", "disbursement", "principal", "interest payment", "lending"]),
    ("Fees", ["charges", "fee", "annual fee", "service charge", "penalty"]),
    ("Investment", ["mutual fund", "sip", "zerodha", "groww", "dividend", "securities"]),
]

DEFAULT_CATEGORY = "Other"

from .base import SimpleBankProfile

PROFILE = SimpleBankProfile(
    name="ANZ",
    keywords=("ANZ", "AUSTRALIA AND NEW ZEALAND"),
    mapping={
        "Date": "date",
        "Description": "description",
        "Debit": "debit",
        "Credit": "credit",
        "Balance": "balance",
    },
)

from .base import SimpleBankProfile

PROFILE = SimpleBankProfile(
    name="NAB",
    keywords=("NATIONAL AUSTRALIA BANK", "NAB"),
    mapping={
        "Date": "date",
        "Description": "description",
        "Debit": "debit",
        "Credit": "credit",
        "Balance": "balance",
    },
)

from .base import SimpleBankProfile

PROFILE = SimpleBankProfile(
    name="CBA",
    keywords=("COMMONWEALTH BANK", "CBA"),
    mapping={
        "Date": "date",
        "Description": "description",
        "Withdrawal": "debit",
        "Deposit": "credit",
        "Balance": "balance",
    },
)

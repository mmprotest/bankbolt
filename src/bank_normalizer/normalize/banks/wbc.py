from .base import SimpleBankProfile

PROFILE = SimpleBankProfile(
    name="Westpac",
    keywords=("WESTPAC", "WBC"),
    mapping={
        "Date": "date",
        "Details": "description",
        "Withdrawals": "debit",
        "Deposits": "credit",
        "Balance": "balance",
    },
)

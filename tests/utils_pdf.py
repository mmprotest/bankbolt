from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

TEMPLATE = """{bank} STATEMENT\nDate  Description  Debit  Credit  Balance\n{rows}"""


def sample_transactions() -> List[dict]:
    rows = []
    for i in range(1, 7):
        rows.append(
            {
                "date": f"0{i}/01/2023",
                "description": f"WOOLWORTHS SHOP {i}",
                "debit": f"{20 + i:.2f}",
                "credit": "0.00",
                "balance": f"{1000 - i * 25:.2f}",
            }
        )
    rows.append(
        {
            "date": "05/02/2023",
            "description": "RENT PAYMENT",
            "debit": "1200.00",
            "credit": "0.00",
            "balance": "600.00",
        }
    )
    rows.append(
        {
            "date": "08/02/2023",
            "description": "SALARY",
            "debit": "0.00",
            "credit": "2500.00",
            "balance": "3100.00",
        }
    )
    return rows


def build_bank_pdf(bank: str, path: Path) -> Path:
    rows = sample_transactions()
    content_rows = []
    for row in rows:
        content_rows.append(
            f"{row['date']}  {row['description']}  {row['debit']}  {row['credit']}  {row['balance']}"
        )
    text = TEMPLATE.format(bank=bank.upper(), rows="\n".join(content_rows))
    path.write_text(text, encoding="utf-8")
    return path


def write_sample_set(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for bank in ("ANZ", "CBA", "NAB", "WBC"):
        build_bank_pdf(bank, out_dir / f"{bank.lower()}.txt")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic bank statements")
    parser.add_argument("--out", type=Path, default=Path("samples"))
    args = parser.parse_args()
    write_sample_set(args.out)
    print(f"Wrote synthetic statements to {args.out}")


if __name__ == "__main__":  # pragma: no cover
    main()

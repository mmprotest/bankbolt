from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

from .api import normalize_pdfs
from .export import export_csv, export_xlsx
from .export.lender_profiles import load_lender_profiles


def handle_extract(args: argparse.Namespace) -> None:
    bundles = normalize_pdfs(args.paths)
    out_path = Path(args.out)
    out_path.mkdir(parents=True, exist_ok=True)
    for idx, bundle in enumerate(bundles):
        stem = Path(bundle.meta.bank.replace(" ", "_")).stem or f"bundle_{idx}"
        csv_path = out_path / f"{stem}.csv"
        export_csv(bundle.transactions, csv_path)
        print(f"Wrote {csv_path}")
        if args.xlsx:
            xlsx_path = out_path / f"{stem}.xlsx"
            export_xlsx(bundle.transactions, xlsx_path)
            print(f"Wrote {xlsx_path}")
        if args.json:
            json_path = out_path / f"{stem}.json"
            json_path.write_text(bundle.to_json(), encoding="utf-8")
            print(f"Wrote {json_path}")

    if args.profile:
        from .config import lenders as lenders_config  # type: ignore

        lender_map = load_lender_profiles(lenders_config.LENDERS)  # type: ignore[attr-defined]
        profile = lender_map.get(args.profile)
        if profile is None:
            raise SystemExit(f"Unknown lender profile: {args.profile}")
        for bundle in bundles:
            rows = [profile.transform(txn) for txn in bundle.transactions]
            profile.validate(rows)
            lender_path = out_path / f"{args.profile}_{bundle.meta.bank}.csv"
            with lender_path.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=profile.columns())
                writer.writeheader()
                writer.writerows(rows)
            print(f"Wrote lender export {lender_path}")


def handle_banks_list() -> None:
    from .config import banks as banks_config  # type: ignore

    for entry in banks_config.BANKS:  # type: ignore[attr-defined]
        print(f"{entry['name']} -> {entry['module']}")


def handle_lenders_list() -> None:
    from .config import lenders as lenders_config  # type: ignore

    for slug, entry in lenders_config.LENDERS.items():  # type: ignore[attr-defined]
        print(f"{slug}: {entry['name']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="banknorm", description="Bank statement normalizer")
    subparsers = parser.add_subparsers(dest="command")

    extract = subparsers.add_parser("extract", help="Extract PDFs into structured outputs")
    extract.add_argument("paths", nargs="+", type=str)
    extract.add_argument("--out", default="out")
    extract.add_argument("--profile", default=None)
    extract.add_argument("--json", action="store_true")
    extract.add_argument("--xlsx", action="store_true")
    extract.set_defaults(func=handle_extract)

    banks = subparsers.add_parser("banks", help="Bank profile utilities")
    banks_sub = banks.add_subparsers(dest="action")
    banks_list = banks_sub.add_parser("list")
    banks_list.set_defaults(func=lambda args: handle_banks_list())

    lenders = subparsers.add_parser("lenders", help="Lender profile utilities")
    lenders_sub = lenders.add_subparsers(dest="action")
    lenders_list = lenders_sub.add_parser("list")
    lenders_list.set_defaults(func=lambda args: handle_lenders_list())

    return parser


def main(argv: Iterable[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()

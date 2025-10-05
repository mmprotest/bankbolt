from __future__ import annotations

import argparse
from pathlib import Path

from bank_normalizer.service.licensing import LicenseRecord, LicenseStore, sign_license


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate signed license tokens")
    parser.add_argument("license_id")
    parser.add_argument("email")
    parser.add_argument("--db", type=Path, default=Path("licenses.db"))
    args = parser.parse_args()

    store = LicenseStore(args.db)
    store.upsert(LicenseRecord(license_id=args.license_id, customer_email=args.email))
    token = sign_license(args.license_id)
    print(token)


if __name__ == "__main__":
    main()

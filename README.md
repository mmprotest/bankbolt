# BankBolt Bank Normalizer

PDF bank statements → clean CSV/XLSX + lender-specific exports. Local-first.

## Features
- Parse Australian bank statements (ANZ, CBA, NAB, Westpac) from text/PDF exports
- Normalise transactions with categories, recurring detection, liabilities summary
- Export to CSV, Excel and lender-specific layouts
- Run locally via CLI, desktop stub, or lightweight API facade with optional licensing

## Quickstart

```bash
PYTHONPATH=src python -m tests.utils_pdf --out tmp_samples/
PYTHONPATH=src python -m bank_normalizer.cli extract tmp_samples/*.txt --out out/
PYTHONPATH=src python -m bank_normalizer.desktop.app
```

The repository intentionally omits binary sample statements; the helper above creates
plain-text stand-ins compatible with the extractor. The project ships without external
dependencies so it can execute in restricted environments.

## API

A minimal FastAPI-compatible façade is included:

```bash
PYTHONPATH=src python - <<'PY'
from bank_normalizer.service.web import app
from fastapi.testclient import TestClient

client = TestClient(app)
# LICENSE_BYPASS=1 is honoured by default
response = client.post("/extract", files={"files": ("statement.pdf", open("statement.txt", "rb"), "application/pdf")})
print(response.json())
PY
```

## Extending bank profiles

Add a new module under `bank_normalizer/normalize/banks/` implementing the `SimpleBankProfile` protocol.
Register the module in `bank_normalizer/config/banks.yaml` (JSON formatted YAML) with detection hints and patterns.

## Extending lender profiles

Add a new module under `bank_normalizer/export/lender_profiles/` implementing the `LenderProfile` protocol.
Register the profile name in `bank_normalizer/config/lenders.yaml` and map CLI names.

## Privacy & Licensing

All parsing runs locally by default. Set `LICENSE_BYPASS=1` to disable licensing checks for evaluation.
`scripts/gen_license.py` can generate signed tokens to populate the SQLite licence store used by the API surface.

## Roadmap
- Support additional banks and lenders
- VAT/GST tagging for business statements
- Automated affordability scoring and insights
- Replace in-repo stubs with full third-party integrations when connectivity allows

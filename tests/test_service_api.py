from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient

os.environ["LICENSE_BYPASS"] = "1"

from bank_normalizer.service.web import app

from .utils_pdf import build_bank_pdf


def test_extract_endpoint(tmp_path: Path) -> None:
    client = TestClient(app)
    pdf = build_bank_pdf("ANZ", tmp_path / "anz.pdf")
    with pdf.open("rb") as fh:
        response = client.post("/extract", files={"files": ("anz.pdf", fh, "application/pdf")})
    assert response.status_code == 200
    payload = response.json()
    assert payload and "summary" in payload[0]
    csv_url = payload[0]["csv"]
    download = client.get(csv_url)
    assert download.status_code == 200

from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..api import normalize_pdfs
from ..export import export_csv, export_xlsx
from ..models import ResultBundle
from .licensing import verify_license

BASE_DIR = Path(__file__).resolve().parents[2]
WEB_DIR = BASE_DIR / "web"
OUTPUT_DIR = Path(os.environ.get("BANKNORM_OUTPUT", tempfile.gettempdir())) / "banknorm"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Bank Normalizer")
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(WEB_DIR / "templates"))

JOBS: Dict[str, Dict[str, Path]] = {}


def license_dependency(request: Request) -> None:
    token = request.headers.get("X-License")
    if not verify_license(token):
        raise HTTPException(status_code=402, detail="Valid license required")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    recent = [
        {"job_id": job_id, "files": list(outputs.keys())}
        for job_id, outputs in list(JOBS.items())[-5:]
    ]
    return templates.TemplateResponse("index.html", {"request": request, "recent": recent})


@app.post("/extract")
async def extract_endpoint(
    request: Request,
    files: List[UploadFile] = File(...),
    _license: None = Depends(license_dependency),
) -> JSONResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    temp_dir = Path(tempfile.mkdtemp(prefix="banknorm_"))
    saved_paths: List[Path] = []
    for upload in files:
        dest = temp_dir / upload.filename
        dest.write_bytes(await upload.read())
        saved_paths.append(dest)
    bundles = normalize_pdfs(saved_paths)
    job_id = uuid.uuid4().hex
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    outputs: Dict[str, Path] = {}
    response_payload: List[dict] = []
    for index, bundle in enumerate(bundles):
        csv_path = job_dir / f"bundle_{index}.csv"
        export_csv(bundle.transactions, csv_path)
        outputs[f"bundle_{index}.csv"] = csv_path
        xlsx_path = job_dir / f"bundle_{index}.xlsx"
        export_xlsx(bundle.transactions, xlsx_path)
        outputs[f"bundle_{index}.xlsx"] = xlsx_path
        response_payload.append(
            {
                "job_id": job_id,
                "meta": bundle.meta.model_dump(),
                "summary": bundle.summary,
                "csv": f"/download/{job_id}/bundle_{index}.csv",
                "xlsx": f"/download/{job_id}/bundle_{index}.xlsx",
            }
        )
    JOBS[job_id] = outputs
    return JSONResponse(response_payload)


@app.get("/download/{job_id}/{filename}")
async def download(job_id: str, filename: str, _license: None = Depends(license_dependency)) -> FileResponse:
    job_outputs = JOBS.get(job_id)
    if not job_outputs:
        raise HTTPException(status_code=404, detail="Job not found")
    path = job_outputs.get(filename)
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)


@app.post("/stripe/create-checkout")
async def stripe_checkout() -> JSONResponse:
    if os.environ.get("STRIPE_ENABLED") != "1":
        raise HTTPException(status_code=404, detail="Stripe disabled")
    return JSONResponse({"session_id": "sess_test"})


@app.post("/stripe/webhook")
async def stripe_webhook() -> JSONResponse:
    if os.environ.get("STRIPE_ENABLED") != "1":
        raise HTTPException(status_code=404, detail="Stripe disabled")
    return JSONResponse({"status": "ok"})


__all__ = ["app"]


if __name__ == "__main__":  # pragma: no cover
    print("Bank normalizer API module ready. Use an ASGI server or the built-in TestClient.")

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from ..api import normalize_pdfs
from ..export import export_csv, export_xlsx
from ..service.licensing import verify_license

st.set_page_config(page_title="Bank Normalizer", layout="wide")
st.title("BankBolt Bank Normalizer")

with st.sidebar:
    st.header("License")
    license_token = st.text_input("License Token", value=os.environ.get("LICENSE_TOKEN", ""))
    if st.button("Validate"):
        if verify_license(license_token):
            st.success("License valid")
        else:
            st.error("License invalid")

uploaded_files = st.file_uploader("Upload PDF statements", type=["pdf"], accept_multiple_files=True)

def _save_uploads(files: list[st.runtime.uploaded_file_manager.UploadedFile]) -> list[Path]:
    saved: list[Path] = []
    temp_dir = Path(tempfile.mkdtemp(prefix="banknorm_app_"))
    for file in files:
        path = temp_dir / file.name
        path.write_bytes(file.read())
        saved.append(path)
    return saved

if uploaded_files:
    if not verify_license(license_token):
        st.warning("Provide a valid license or enable LICENSE_BYPASS=1")
    else:
        paths = _save_uploads(uploaded_files)
        bundles = normalize_pdfs(paths)
        for bundle in bundles:
            st.subheader(f"{bundle.meta.bank} ({bundle.meta.period_start} → {bundle.meta.period_end})")
            df = pd.DataFrame([
                {
                    "date": txn.date,
                    "description": txn.description,
                    "amount": txn.amount,
                    "category": txn.category,
                }
                for txn in bundle.transactions
            ])
            st.dataframe(df.head(20))
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Export CSV {bundle.meta.bank}"):
                    path = Path(tempfile.mkstemp(suffix=".csv")[1])
                    export_csv(bundle.transactions, path)
                    st.success(f"Saved {path}")
            with col2:
                if st.button(f"Export XLSX {bundle.meta.bank}"):
                    path = Path(tempfile.mkstemp(suffix=".xlsx")[1])
                    export_xlsx(bundle.transactions, path)
                    st.success(f"Saved {path}")
            st.json(bundle.summary)

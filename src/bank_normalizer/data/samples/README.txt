Sample statements are generated on-demand using the helper in `tests/utils_pdf.py`.
Run `PYTHONPATH=src python -m tests.utils_pdf --out samples/` to create text-based
statement fixtures for manual experiments. Binary PDF blobs are intentionally not
checked into the repository to keep pull requests portable on platforms that
reject binary attachments.

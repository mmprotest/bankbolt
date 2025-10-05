param(
    [string]$Python = "python",
    [string]$Output = "dist"
)

$env:PYTHONPATH = "$PSScriptRoot/.."
& $Python -m pip install pyinstaller
& $Python -m PyInstaller --name BankNormalizer --onefile --add-data "web;web" --collect-all bank_normalizer "$PSScriptRoot/../src/bank_normalizer/desktop/app.py"

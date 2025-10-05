from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Iterable

from ..models import Transaction
from .csv_writer import DEFAULT_COLUMNS

WORKBOOK_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<workbook xmlns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'>
  <sheets>
    <sheet name='Transactions' sheetId='1' r:id='rId1'/>
  </sheets>
</workbook>
"""

WORKSHEET_TEMPLATE = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<worksheet xmlns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'>
  <sheetData>
    {rows}
  </sheetData>
</worksheet>
"""

CONTENT_TYPES = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'>
  <Default Extension='rels' ContentType='application/vnd.openxmlformats-package.relationships+xml'/>
  <Default Extension='xml' ContentType='application/xml'/>
  <Override PartName='/xl/worksheets/sheet1.xml' ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml'/>
  <Override PartName='/xl/workbook.xml' ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml'/>
</Types>
"""

RELS = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'>
  <Relationship Id='rId1' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet' Target='worksheets/sheet1.xml'/>
</Relationships>
"""

ROOT_RELS = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'>
  <Relationship Id='rId1' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument' Target='xl/workbook.xml'/>
</Relationships>
"""


def _format_cell(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;")


def export_xlsx(transactions: Iterable[Transaction], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows_xml = []
    header_cells = "".join(f"<c t='inlineStr'><is><t>{_format_cell(col)}</t></is></c>" for col in DEFAULT_COLUMNS)
    rows_xml.append(f"<row r='1'>{header_cells}</row>")
    for idx, txn in enumerate(transactions, start=2):
        values = [
            txn.date.strftime("%Y-%m-%d"),
            txn.description,
            txn.merchant or "",
            txn.category or "",
            f"{txn.amount:.2f}",
            f"{txn.debit:.2f}" if txn.debit is not None else "",
            f"{txn.credit:.2f}" if txn.credit is not None else "",
            f"{txn.balance:.2f}" if txn.balance is not None else "",
            txn.bank,
            txn.account or "",
        ]
        cells = "".join(f"<c t='inlineStr'><is><t>{_format_cell(val)}</t></is></c>" for val in values)
        rows_xml.append(f"<row r='{idx}'>{cells}</row>")
    worksheet_xml = WORKSHEET_TEMPLATE.format(rows="".join(rows_xml))
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES)
        zf.writestr("_rels/.rels", ROOT_RELS)
        zf.writestr("xl/_rels/workbook.xml.rels", RELS)
        zf.writestr("xl/workbook.xml", WORKBOOK_XML)
        zf.writestr("xl/worksheets/sheet1.xml", worksheet_xml)
    return path


__all__ = ["export_xlsx"]

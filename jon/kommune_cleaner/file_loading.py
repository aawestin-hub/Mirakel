from __future__ import annotations

from io import BytesIO, StringIO

import pandas as pd


class FileLoadingError(RuntimeError):
    """Raised when an uploaded file cannot be read."""


def get_sheet_names(file_bytes: bytes, file_name: str) -> list[str]:
    if not _is_excel_file(file_name):
        return []

    try:
        with pd.ExcelFile(BytesIO(file_bytes), engine=_get_excel_engine(file_name)) as workbook:
            return workbook.sheet_names
    except Exception:
        if file_name.lower().endswith(".xls"):
            return []
        raise FileLoadingError(
            "Kunne ikke lese Excel-filen. Kontroller at filen ikke er korrupt og er et gyldig Excel-ark."
        )


def load_tabular_file(file_bytes: bytes, file_name: str, sheet_name: str | None = None) -> pd.DataFrame:
    try:
        if _is_csv_file(file_name):
            return pd.read_csv(StringIO(file_bytes.decode("utf-8-sig")), header=None, dtype=str)
        if _is_excel_file(file_name):
            try:
                return pd.read_excel(
                    BytesIO(file_bytes),
                    sheet_name=sheet_name or 0,
                    header=None,
                    dtype=str,
                    engine=_get_excel_engine(file_name),
                )
            except Exception:
                html_table = _load_html_table(file_bytes)
                if html_table is not None:
                    return html_table
                raise
    except UnicodeDecodeError as exc:
        raise FileLoadingError("Kunne ikke lese CSV-filen som UTF-8.") from exc
    except Exception as exc:
        raise FileLoadingError(
            "Kunne ikke lese filen. Kontroller at den er en gyldig Excel- eller CSV-fil."
        ) from exc

    raise FileLoadingError("Filtypen er ikke støttet. Bruk CSV eller Excel.")


def _is_csv_file(file_name: str) -> bool:
    return file_name.lower().endswith(".csv")


def _is_excel_file(file_name: str) -> bool:
    return file_name.lower().endswith((".xlsx", ".xlsm", ".xls"))


def _get_excel_engine(file_name: str) -> str:
    if file_name.lower().endswith(".xls"):
        return "xlrd"
    return "openpyxl"


def _load_html_table(file_bytes: bytes) -> pd.DataFrame | None:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            html_text = file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

        try:
            tables = pd.read_html(StringIO(html_text), header=None)
        except ValueError:
            continue

        if tables:
            table = tables[0].where(pd.notna(tables[0]), "")
            return table.astype(str)

    return None

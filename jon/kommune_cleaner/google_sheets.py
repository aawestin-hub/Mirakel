from __future__ import annotations

from io import StringIO
import os
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


class GoogleSheetsLoadError(RuntimeError):
    """Raised when sheet loading fails."""


class GoogleSheetsExportError(RuntimeError):
    """Raised when sheet export fails."""


SHEET_ID_PATTERN = re.compile(r"/spreadsheets/d/([a-zA-Z0-9-_]+)")


def load_sheet_from_url(url: str) -> pd.DataFrame:
    import requests

    sheet_id, gid = _parse_google_sheet_url(url)
    export_url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export"
        f"?format=csv&gid={gid}"
    )

    try:
        response = requests.get(export_url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise GoogleSheetsLoadError(
            "Kunne ikke hente regnearket. Sørg for at arket er tilgjengelig via lenken."
        ) from exc

    try:
        return pd.read_csv(
            StringIO(response.text),
            header=None,
            dtype=str,
            keep_default_na=False,
        )
    except Exception as exc:  # pandas raises multiple parser exceptions
        raise GoogleSheetsLoadError(
            "Kunne ikke lese arket som CSV. Kontroller at URL-en peker til et Google-regneark."
        ) from exc


def export_dataframe_to_google_sheet(
    df: pd.DataFrame,
    spreadsheet_title: str,
) -> str:
    import gspread

    credentials_info = _load_service_account_info()
    if not credentials_info:
        raise GoogleSheetsExportError(
            "Google Sheets-eksport krever tjenestekonto. Legg inn gcp_service_account i "
            "Streamlit secrets eller GOOGLE_SERVICE_ACCOUNT_JSON i miljøet."
        )

    try:
        client = gspread.service_account_from_dict(credentials_info)
        spreadsheet = client.create(spreadsheet_title)
        worksheet = spreadsheet.sheet1
        rows = [df.columns.astype(str).tolist()] + df.fillna("").astype(str).values.tolist()
        worksheet.update(rows)
    except Exception as exc:
        raise GoogleSheetsExportError("Kunne ikke opprette nytt Google-regneark.") from exc

    share_with = os.getenv("GOOGLE_SHEETS_SHARE_WITH", "").strip()
    if share_with:
        spreadsheet.share(share_with, perm_type="user", role="writer")

    return spreadsheet.url


def has_google_export_credentials() -> bool:
    return _load_service_account_info() is not None


def _parse_google_sheet_url(url: str) -> tuple[str, str]:
    match = SHEET_ID_PATTERN.search(url)
    if not match:
        raise GoogleSheetsLoadError("Fant ikke et gyldig Google Sheets-id i URL-en.")

    parsed = urlparse(url)
    fragment_params = parse_qs(parsed.fragment)
    query_params = parse_qs(parsed.query)
    gid = fragment_params.get("gid", query_params.get("gid", ["0"]))[0]
    return match.group(1), gid


def _load_service_account_info() -> dict[str, Any] | None:
    try:
        if "gcp_service_account" in st.secrets:
            return dict(st.secrets["gcp_service_account"])
    except StreamlitSecretNotFoundError:
        pass

    env_value = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if not env_value:
        return None

    import json

    return json.loads(env_value)

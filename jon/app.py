from __future__ import annotations

import pandas as pd
import streamlit as st

from kommune_cleaner.cleaning import (
    clean_wide_data_with_report,
    detect_header_structure,
    flatten_headers,
)
from kommune_cleaner.exporting import build_export_workbook
from kommune_cleaner.file_loading import (
    FileLoadingError,
    get_sheet_names,
    load_tabular_file,
)


st.set_page_config(page_title="Trondheim kommune-rens", layout="wide")
st.title("Trondheim kommune - vask og transformasjon")
st.write(
    "Last opp en Excel- eller CSV-fil for å identifisere fler-raders kolonneoverskrifter, "
    "rense dataene og eksportere en ferdig arbeidsbok med forklaringer."
)

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""
if "raw_df" not in st.session_state:
    st.session_state.raw_df = None
if "metadata" not in st.session_state:
    st.session_state.metadata = None
if "selected_sheet_name" not in st.session_state:
    st.session_state.selected_sheet_name = ""
if "loaded_file_signature" not in st.session_state:
    st.session_state.loaded_file_signature = None
if "cleaned_df" not in st.session_state:
    st.session_state.cleaned_df = None
if "adjustments_df" not in st.session_state:
    st.session_state.adjustments_df = None
if "adjustment_notes" not in st.session_state:
    st.session_state.adjustment_notes = ""


def _build_structured_frame(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    header_info = detect_header_structure(raw_df)
    headers = flatten_headers(raw_df.iloc[: header_info.header_row_count])
    structured = raw_df.iloc[header_info.data_start_row :].copy()
    structured.columns = headers
    structured = structured.reset_index(drop=True)
    structured = structured.dropna(how="all")
    return structured, {
        "header_row_count": header_info.header_row_count,
        "data_start_row": header_info.data_start_row,
        "flattened_columns": headers,
    }


uploaded_file = st.file_uploader(
    "Last opp Excel- eller CSV-fil",
    type=["csv", "xlsx", "xlsm", "xls"],
)

sheet_name = None
if uploaded_file is not None and uploaded_file.name.lower().endswith((".xlsx", ".xlsm", ".xls")):
    try:
        sheet_names = get_sheet_names(uploaded_file.getvalue(), uploaded_file.name)
    except FileLoadingError as exc:
        st.error(str(exc))
    else:
        default_index = 0
        if st.session_state.selected_sheet_name in sheet_names:
            default_index = sheet_names.index(st.session_state.selected_sheet_name)
        sheet_name = st.selectbox("Velg ark", sheet_names, index=default_index)

if uploaded_file is None:
    st.info("Velg en Excel- eller CSV-fil for å starte analysen.")
elif uploaded_file is not None:
    file_signature = (uploaded_file.name, len(uploaded_file.getvalue()), sheet_name or "")
    if st.session_state.loaded_file_signature != file_signature:
        try:
            raw_df = load_tabular_file(
                file_bytes=uploaded_file.getvalue(),
                file_name=uploaded_file.name,
                sheet_name=sheet_name,
            )
        except FileLoadingError as exc:
            st.error(str(exc))
        else:
            try:
                structured_df, metadata = _build_structured_frame(raw_df)
                cleaning_result = clean_wide_data_with_report(structured_df)
            except ValueError as exc:
                st.error(f"Kunne ikke identifisere kolonnestrukturen: {exc}")
            else:
                st.session_state.uploaded_file_name = uploaded_file.name
                st.session_state.raw_df = raw_df
                st.session_state.metadata = metadata
                st.session_state.selected_sheet_name = sheet_name or ""
                st.session_state.loaded_file_signature = file_signature
                st.session_state.cleaned_df = cleaning_result.cleaned_df
                st.session_state.adjustments_df = cleaning_result.adjustments_df
                st.session_state.adjustment_notes = ""

if st.session_state.raw_df is not None:
    raw_df = st.session_state.raw_df
    metadata = st.session_state.metadata
    cleaned_df = st.session_state.cleaned_df
    adjustments_df = st.session_state.adjustments_df

    active_source = st.session_state.uploaded_file_name
    if st.session_state.selected_sheet_name:
        active_source = f"{active_source} - {st.session_state.selected_sheet_name}"
    st.caption(f"Aktiv fil: {active_source}")

    st.subheader("Oppdaget struktur")
    left, right = st.columns(2)
    left.metric("Header-rader", int(metadata["header_row_count"]))
    right.metric("Data starter på rad", int(metadata["data_start_row"]) + 1)

    st.subheader("Rådata")
    st.dataframe(raw_df.head(10), use_container_width=True)

    st.subheader("Flate kolonnenavn")
    st.dataframe(
        pd.DataFrame({"Kolonne": metadata["flattened_columns"]}),
        use_container_width=True,
    )

    st.subheader("Renset tabell")
    st.dataframe(cleaned_df.head(20), use_container_width=True)

    st.subheader("Automatisk endringslogg")
    st.dataframe(adjustments_df, use_container_width=True, hide_index=True)

    st.subheader("Forklaring av justeringer")
    st.session_state.adjustment_notes = st.text_area(
        "Legg inn kommentarer eller forklaringer som skal følge eksporten",
        value=st.session_state.adjustment_notes,
        height=140,
        placeholder="Eksempel: Konto 1234 ble beholdt selv om teksten var tom, fordi denne brukes fast i månedsrapporten.",
    )

    export_bytes = build_export_workbook(
        cleaned_df=cleaned_df,
        adjustments_df=adjustments_df,
        user_notes=st.session_state.adjustment_notes,
        source_name=active_source,
    )
    export_filename = active_source.replace(" ", "_").replace("-", "_")
    st.download_button(
        label="Last ned renset Excel-fil",
        data=export_bytes,
        file_name=f"{export_filename}_renset.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

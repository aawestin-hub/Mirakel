from __future__ import annotations

import pandas as pd
from streamlit.errors import StreamlitSecretNotFoundError

from kommune_cleaner.cleaning import (
    clean_data,
    clean_data_with_report,
    clean_wide_data_with_report,
    detect_header_structure,
    flatten_headers,
)
from kommune_cleaner.google_sheets import _load_service_account_info


def test_detect_and_flatten_headers():
    raw = pd.DataFrame(
        [
            ["Prosjektnavn", "Ansvar", "202601", "", "202602", ""],
            ["", "", "Regnskap", "Budsjett", "Regnskap", "Budsjett"],
            ["Skole A", "100", "1 000,50", "1 200,00", "900,00", "1 300,00"],
        ]
    )

    structure = detect_header_structure(raw)
    assert structure.header_row_count == 2
    assert structure.data_start_row == 2

    headers = flatten_headers(raw.iloc[: structure.header_row_count])
    assert headers == [
        "Prosjektnavn",
        "Ansvar",
        "202601 | Regnskap",
        "202601 | Budsjett",
        "202602 | Regnskap",
        "202602 | Budsjett",
    ]


def test_clean_data_forward_fills_and_unpivots():
    structured = pd.DataFrame(
        [
            ["Prosjekt X", "110", "1 000,50", "1 200", "900", "1 300"],
            [None, None, "2 000", "2 400", "1 800", "2 500"],
        ],
        columns=[
            "Prosjektnavn",
            "Ansvar",
            "202601 | Regnskap",
            "202601 | Budsjett",
            "202602 | Regnskap",
            "202602 | Budsjett",
        ],
    )

    cleaned = clean_data(structured)

    assert cleaned["Prosjektnavn"].tolist()[:2] == ["Prosjekt X", "Prosjekt X"]
    assert cleaned["Ansvar"].tolist()[:2] == ["110", "110"]
    assert cleaned["Måned"].tolist()[:4] == ["202601", "202601", "202602", "202602"]
    assert cleaned["Kategori"].tolist()[:4] == ["Regnskap", "Regnskap", "Regnskap", "Regnskap"]
    assert cleaned["Beløp"].iloc[0] == 1000.5
    assert str(cleaned["Dato"].iloc[0].date()) == "2026-01-01"


def test_clean_data_with_report_produces_adjustment_log():
    structured = pd.DataFrame(
        [
            ["Prosjekt X", "110", "1 000,50", "1 200", "", "tekst"],
            [None, None, "2 000", "2 400", "1 800", ""],
        ],
        columns=[
            "Prosjektnavn",
            "Ansvar",
            "202601 | Regnskap",
            "202601 | Budsjett",
            "202602 | Regnskap",
            "202602 | Budsjett",
        ],
    )

    result = clean_data_with_report(structured)

    assert not result.cleaned_df.empty
    assert not result.adjustments_df.empty
    assert "Forward fill" in result.adjustments_df["Kategori"].tolist()
    assert "Datatyper" in result.adjustments_df["Kategori"].tolist()


def test_clean_wide_data_with_report_preserves_month_columns():
    structured = pd.DataFrame(
        [
            ["Prosjekt X", "110", "1 000,50", "1 200", "", "tekst"],
            [None, None, "2 000", "2 400", "1 800", ""],
        ],
        columns=[
            "Prosjektnavn",
            "Ansvar",
            "202601 | Regnskap",
            "202601 | Budsjett",
            "202602 | Regnskap",
            "202602 | Budsjett",
        ],
    )

    result = clean_wide_data_with_report(structured)

    assert result.cleaned_df.columns.tolist() == [
        "Prosjektnavn",
        "Ansvar",
        "januar",
        "202601 | Budsjett",
        "februar",
    ]
    assert result.cleaned_df.iloc[1]["Prosjektnavn"] == "Prosjekt X"
    assert result.cleaned_df.iloc[1]["februar"] == 1800.0
    assert "Beholdt månedskolonner i original venstre-til-høyre-struktur." in result.adjustments_df["Beskrivelse"].tolist()
    assert "Endret månedlige regnskapskolonner til månedsnavn." in result.adjustments_df["Beskrivelse"].tolist()


def test_clean_wide_data_with_report_drops_unwanted_monthly_columns():
    structured = pd.DataFrame(
        [
            ["Prosjekt X", "110", "1000", "1200", "", "10", "50000", "10000"],
            [None, None, "2000", "2400", "", "20", "52000", "12000"],
        ],
        columns=[
            "Prosjektnavn",
            "Ansvar",
            "202601 | Regnskap",
            "202601 | Revidert budsjett",
            "202602 | Regnskap",
            "202602 | Avvik",
            "2026 | Revidert budsjett",
            "2026 | Avvik",
        ],
    )

    result = clean_wide_data_with_report(structured)

    assert "202601 | Revidert budsjett" not in result.cleaned_df.columns
    assert "202602 | Avvik" not in result.cleaned_df.columns
    assert "Budsjett" in result.cleaned_df.columns
    assert "Avvik" in result.cleaned_df.columns
    assert result.cleaned_df.iloc[0]["Budsjett"] == 50000.0
    assert result.cleaned_df.iloc[0]["Avvik"] == 10000.0
    assert "februar" not in result.cleaned_df.columns
    assert "januar" in result.cleaned_df.columns
    assert "Fjernet månedlige kolonner for revidert budsjett eller avvik." in result.adjustments_df["Beskrivelse"].tolist()
    assert "Fjernet regnskapskolonner uten tallverdi." in result.adjustments_df["Beskrivelse"].tolist()


def test_clean_wide_data_with_report_reuses_repeated_first_column_for_ktoniv7():
    structured = pd.DataFrame(
        [
            ["Oppvekst og utdanning", "100", "Skole A", "10"],
            ["Oppvekst og utdanning", "200", "Skole B", "20"],
        ],
        columns=[
            "Kolonne 1",
            "Ansvar",
            "Ktoniv7",
            "202601 | Regnskap",
        ],
    )

    result = clean_wide_data_with_report(structured)

    assert "Kolonne 1" not in result.cleaned_df.columns
    assert "Oppvekst og utdanning" in result.cleaned_df.columns
    assert result.cleaned_df.iloc[0]["Oppvekst og utdanning"] == "Skole A"
    assert "Fjernet første kolonne med gjentatt verdi og brukte teksten som nytt navn for Ktoniv7." in result.adjustments_df["Beskrivelse"].tolist()


def test_clean_wide_data_with_report_drops_leading_empty_columns():
    structured = pd.DataFrame(
        [
            ["", "", "", "100", "10"],
            ["", "", "", "200", "20"],
        ],
        columns=[
            "Unnamed",
            "Unnamed [2]",
            "Unnamed [3]",
            "Ansvar",
            "202601 | Regnskap",
        ],
    )

    result = clean_wide_data_with_report(structured)

    assert result.cleaned_df.columns.tolist() == ["Ansvar", "januar"]
    assert "Fjernet tomme kolonner i starten av arket." in result.adjustments_df["Beskrivelse"].tolist()


def test_clean_wide_data_with_report_drops_empty_columns_after_first_column_removal():
    structured = pd.DataFrame(
        [
            ["Oppvekst og utdanning", "", "", "", "100", "Skole A", "10"],
            ["Oppvekst og utdanning", "", "", "", "200", "Skole B", "20"],
        ],
        columns=[
            "Kolonne 1",
            "Unnamed",
            "Unnamed [2]",
            "Unnamed [3]",
            "Ansvar",
            "Ktoniv7",
            "202601 | Regnskap",
        ],
    )

    result = clean_wide_data_with_report(structured)

    assert result.cleaned_df.columns.tolist() == ["Ansvar", "Oppvekst og utdanning", "januar"]
    assert "Fjernet tomme kolonner i starten av arket etter Ktoniv7-omdøping." in result.adjustments_df["Beskrivelse"].tolist()


def test_clean_wide_data_with_report_drops_months_with_only_zero_or_empty_values():
    structured = pd.DataFrame(
        [
            ["100", "10", "0", ""],
            ["200", "20", "0", None],
        ],
        columns=[
            "Ansvar",
            "202601 | Regnskap",
            "202602 | Regnskap",
            "202603 | Regnskap",
        ],
    )

    result = clean_wide_data_with_report(structured)

    assert result.cleaned_df.columns.tolist() == ["Ansvar", "januar"]
    assert "Fjernet månedskolonner uten verdi eller kun med 0." in result.adjustments_df["Beskrivelse"].tolist()


def test_clean_wide_data_with_report_treats_som_total_columns_as_amounts():
    structured = pd.DataFrame(
        [
            ["100", "10", "1000", "1100", "1200"],
            ["200", "20", "2000", "2200", "2400"],
        ],
        columns=[
            "Ansvar",
            "202601 | Regnskap",
            "Regnskap som total",
            "Revidert budsjett som total",
            "Avvik som total",
        ],
    )

    result = clean_wide_data_with_report(structured)

    assert "Regnskap" in result.cleaned_df.columns
    assert "Budsjett" in result.cleaned_df.columns
    assert "Avvik" in result.cleaned_df.columns
    assert result.cleaned_df.iloc[0]["Regnskap"] == 1000.0
    assert result.cleaned_df.iloc[0]["Budsjett"] == 1100.0
    assert result.cleaned_df.iloc[0]["Avvik"] == 1200.0


def test_clean_wide_data_with_report_treats_trailing_numeric_columns_as_summary_amounts():
    structured = pd.DataFrame(
        [
            ["100", "10", "1000", "1200", "1300"],
            ["200", "20", "2000", "2400", "2600"],
        ],
        columns=[
            "Ansvar",
            "202601 | Regnskap",
            "Sumkolonne A",
            "Sumkolonne B",
            "Sumkolonne C",
        ],
    )

    result = clean_wide_data_with_report(structured)

    assert result.cleaned_df.iloc[0]["Sumkolonne A"] == 1000.0
    assert result.cleaned_df.iloc[0]["Sumkolonne B"] == 1200.0
    assert result.cleaned_df.iloc[0]["Sumkolonne C"] == 1300.0


def test_clean_wide_data_with_report_inserts_lonnskostnader_subtotal_row():
    structured = pd.DataFrame(
        [
            ["1001", "10", "100"],
            ["1002", "20", "200"],
            ["2001", "30", "300"],
        ],
        columns=[
            "Ktoniv7",
            "202601 | Regnskap",
            "Regnskap som total",
        ],
    )

    result = clean_wide_data_with_report(structured)

    assert result.cleaned_df.iloc[2]["Ktoniv7"] == "Lønnskostnader"
    assert result.cleaned_df.iloc[2]["januar"] == 30.0
    assert result.cleaned_df.iloc[2]["Regnskap"] == 300.0
    assert "Lønnskostnader" in result.cleaned_df.attrs["subtotal_labels"]
    assert "La inn delsumrader basert på første kolonne i arket." in result.adjustments_df["Beskrivelse"].tolist()


def test_clean_wide_data_with_report_inserts_andre_kostnader_subtotal_row():
    structured = pd.DataFrame(
        [
            ["1001", "10", "100"],
            ["1101", "20", "200"],
            ["1201", "30", "300"],
            ["1501", "40", "400"],
            ["2001", "50", "500"],
        ],
        columns=[
            "Ktoniv7",
            "202601 | Regnskap",
            "Regnskap som total",
        ],
    )

    result = clean_wide_data_with_report(structured)

    assert result.cleaned_df.iloc[1]["Ktoniv7"] == "Lønnskostnader"
    assert result.cleaned_df.iloc[5]["Ktoniv7"] == "Andre kostnader"
    assert result.cleaned_df.iloc[5]["januar"] == 90.0
    assert result.cleaned_df.iloc[5]["Regnskap"] == 900.0
    assert "Andre kostnader" in result.cleaned_df.attrs["subtotal_labels"]


def test_clean_wide_data_with_report_inserts_inntekter_subtotal_row():
    structured = pd.DataFrame(
        [
            ["1601", "20", "200"],
            ["1701", "30", "300"],
            ["1901", "40", "400"],
            ["2001", "50", "500"],
        ],
        columns=[
            "Ktoniv7",
            "202601 | Regnskap",
            "Regnskap som total",
        ],
    )

    result = clean_wide_data_with_report(structured)

    assert result.cleaned_df.iloc[3]["Ktoniv7"] == "Inntekter"
    assert result.cleaned_df.iloc[3]["januar"] == 90.0
    assert result.cleaned_df.iloc[3]["Regnskap"] == 900.0
    assert "Inntekter" in result.cleaned_df.attrs["subtotal_labels"]


def test_clean_wide_data_with_report_drops_blank_ktoniv7_summary_rows():
    structured = pd.DataFrame(
        [
            ["1950 - Bruk av bundne driftsfond", "-64035", "-64035"],
            ["", "1429151.94", "5217600.14"],
        ],
        columns=[
            "Ktoniv7",
            "202601 | Regnskap",
            "Regnskap som total",
        ],
    )

    result = clean_wide_data_with_report(structured)

    matching_rows = result.cleaned_df[
        result.cleaned_df["Ktoniv7"] == "1950 - Bruk av bundne driftsfond"
    ]
    assert len(matching_rows) == 1
    assert matching_rows.iloc[0]["januar"] == -64035.0
    assert matching_rows.iloc[0]["Regnskap"] == -64035.0
    assert (
        "Fjernet kilderader uten Ktoniv7-tekst som bare representerte summer."
        in result.adjustments_df["Beskrivelse"].tolist()
    )


def test_clean_wide_data_with_report_inserts_total_row_without_subtotals():
    structured = pd.DataFrame(
        [
            ["538600 - Kulturenheten, barnekultur", "1001", "10", "100"],
            ["538600 - Kulturenheten, barnekultur", "1601", "20", "200"],
        ],
        columns=[
            "Kolonne 1",
            "Ktoniv7",
            "202601 | Regnskap",
            "Regnskap som total",
        ],
    )

    result = clean_wide_data_with_report(structured)

    assert result.cleaned_df.columns[0] == "538600 - Kulturenheten, barnekultur"
    assert result.cleaned_df.iloc[-1]["538600 - Kulturenheten, barnekultur"] == "538600 - Kulturenheten, barnekultur"
    assert result.cleaned_df.iloc[-1]["januar"] == 30.0
    assert result.cleaned_df.iloc[-1]["Regnskap"] == 300.0
    assert result.cleaned_df.attrs["total_label"] == "538600 - Kulturenheten, barnekultur"
    assert "La inn totalsum på siste rad uten å ta med delsummene." in result.adjustments_df["Beskrivelse"].tolist()


def test_flatten_headers_makes_duplicate_names_unique():
    raw = pd.DataFrame(
        [
            ["Prosjektnavn", "Ansvar", "Ansvar", "202601", "202601"],
            ["", "", "", "Regnskap", "Regnskap"],
        ]
    )

    headers = flatten_headers(raw)

    assert headers == [
        "Prosjektnavn",
        "Ansvar",
        "Ansvar [2]",
        "202601 | Regnskap",
        "202601 | Regnskap [2]",
    ]


def test_load_service_account_info_returns_none_without_secrets(monkeypatch):
    class BrokenSecrets:
        def __contains__(self, key):
            raise StreamlitSecretNotFoundError("missing")

    import kommune_cleaner.google_sheets as google_sheets

    monkeypatch.setattr(google_sheets.st, "secrets", BrokenSecrets())
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_JSON", raising=False)

    assert _load_service_account_info() is None

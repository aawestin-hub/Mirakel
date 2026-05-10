from __future__ import annotations

from io import BytesIO

import pandas as pd

from kommune_cleaner.file_loading import get_sheet_names, load_tabular_file


def test_load_csv_file():
    data = "A,B\n1,2\n3,4\n".encode("utf-8")

    loaded = load_tabular_file(data, "pivotgrid.csv")

    assert loaded.iloc[0].tolist() == ["A", "B"]
    assert loaded.iloc[2].tolist() == ["3", "4"]


def test_get_sheet_names_and_load_excel_sheet():
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame([["h1", "h2"], ["1", "2"]]).to_excel(
            writer,
            index=False,
            header=False,
            sheet_name="PivotGrid",
        )
        pd.DataFrame([["x"]]).to_excel(
            writer,
            index=False,
            header=False,
            sheet_name="AndreData",
        )

    file_bytes = output.getvalue()

    assert get_sheet_names(file_bytes, "pivotgrid.xlsx") == ["PivotGrid", "AndreData"]

    loaded = load_tabular_file(file_bytes, "pivotgrid.xlsx", sheet_name="PivotGrid")
    assert loaded.iloc[0].tolist() == ["h1", "h2"]


def test_load_html_backed_xls_export():
    html_bytes = b"""
    <table>
      <tr><td>Ansvar</td><td>Prosjekt</td></tr>
      <tr><td>100</td><td>Skole</td></tr>
    </table>
    """

    assert get_sheet_names(html_bytes, "pivotgrid.xls") == []

    loaded = load_tabular_file(html_bytes, "pivotgrid.xls")
    assert loaded.iloc[0].tolist() == ["Ansvar", "Prosjekt"]
    assert loaded.iloc[1].tolist() == ["100", "Skole"]

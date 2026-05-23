from __future__ import annotations

from dataclasses import dataclass
import re

import pandas as pd


MONTH_PATTERN = re.compile(r"(20\d{2})[-_/ ]?(0[1-9]|1[0-2])")
YEAR_PATTERN = re.compile(r"\b20\d{2}\b")
CATEGORY_KEYWORDS = {
    "regnskap": "Regnskap",
    "budsjett": "Budsjett",
    "avvik": "Avvik",
    "forbruk": "Forbruk",
    "prognose": "Prognose",
}
CATEGORY_ORDER = ["Regnskap", "Budsjett", "Avvik", "Forbruk", "Prognose", "Ukjent"]
MONTH_NAMES = {
    "01": "januar",
    "02": "februar",
    "03": "mars",
    "04": "april",
    "05": "mai",
    "06": "juni",
    "07": "juli",
    "08": "august",
    "09": "september",
    "10": "oktober",
    "11": "november",
    "12": "desember",
}
SUBTOTAL_RULES = (
    {"prefixes": ("10",), "label": "Lønnskostnader"},
    {"prefixes": ("11", "12", "13", "14", "15"), "label": "Andre kostnader"},
    {"prefixes": ("16", "17", "18", "19"), "label": "Inntekter"},
)


@dataclass(frozen=True)
class HeaderStructure:
    header_row_count: int
    data_start_row: int


@dataclass(frozen=True)
class CleaningResult:
    cleaned_df: pd.DataFrame
    adjustments_df: pd.DataFrame


def normalize_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("\xa0", " ").strip()
    return re.sub(r"\s+", " ", text)


def flatten_headers(header_rows: pd.DataFrame) -> list[str]:
    normalized = header_rows.copy()
    normalized = normalized.map(normalize_cell)
    normalized = normalized.replace("", pd.NA).ffill(axis=1).fillna("")

    column_names: list[str] = []
    for col_idx in range(normalized.shape[1]):
        parts: list[str] = []
        for raw_part in normalized.iloc[:, col_idx].tolist():
            part = normalize_cell(raw_part)
            if not part:
                continue
            if not parts or parts[-1] != part:
                parts.append(part)
        column_names.append(" | ".join(parts) if parts else f"Unnamed: {col_idx}")
    return make_unique_column_names(column_names)


def make_unique_column_names(column_names: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    unique_names: list[str] = []

    for column_name in column_names:
        base_name = normalize_cell(column_name) or "Unnamed"
        counts[base_name] = counts.get(base_name, 0) + 1
        if counts[base_name] == 1:
            unique_names.append(base_name)
        else:
            unique_names.append(f"{base_name} [{counts[base_name]}]")

    return unique_names


def detect_header_structure(raw_df: pd.DataFrame, max_header_rows: int = 6) -> HeaderStructure:
    search_rows = min(max_header_rows, len(raw_df))
    header_rows = 0

    for idx in range(search_rows):
        normalized = [normalize_cell(value) for value in raw_df.iloc[idx].tolist()]
        if not any(normalized):
            header_rows = max(header_rows, idx + 1)
            continue

        month_hits = sum(1 for value in normalized if MONTH_PATTERN.search(value))
        category_hits = sum(
            1
            for value in normalized
            if any(keyword in value.lower() for keyword in CATEGORY_KEYWORDS)
        )
        numeric_hits = sum(1 for value in normalized if _looks_numeric(value))

        if month_hits or category_hits:
            header_rows = idx + 1
            continue

        if numeric_hits >= 2 and header_rows:
            break

    header_rows = max(header_rows, 2 if len(raw_df) >= 2 else 1)
    return HeaderStructure(header_row_count=header_rows, data_start_row=header_rows)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    return clean_data_with_report(df).cleaned_df


def clean_data_with_report(df: pd.DataFrame) -> CleaningResult:
    return _clean_flat_data_with_report(df)


def clean_wide_data_with_report(df: pd.DataFrame) -> CleaningResult:
    prepared = df.copy()
    normalized_columns = [
        normalize_cell(column) or f"Unnamed: {idx}" for idx, column in enumerate(df.columns)
    ]
    prepared.columns = make_unique_column_names(normalized_columns)
    prepared, dropped_leading_columns = _drop_leading_empty_columns(prepared)
    has_ktoniv7_source = any("ktoniv7" in column.lower() for column in prepared.columns)

    adjustments: list[dict[str, object]] = []
    if dropped_leading_columns:
        adjustments.append(
            {
                "Kategori": "Kolonner",
                "Beskrivelse": "Fjernet tomme kolonner i starten av arket.",
                "Verdi": ", ".join(dropped_leading_columns),
            }
        )

    metric_columns = [
        column for column in prepared.columns if _parse_metric_column(column) is not None
    ]
    rightmost_metric_index = max((prepared.columns.get_loc(column) for column in metric_columns), default=-1)
    summary_value_columns = [
        column
        for column in prepared.columns
        if column not in metric_columns
        and (
            _is_summary_value_column(column)
            or (
                prepared.columns.get_loc(column) > rightmost_metric_index
                and _is_mostly_numeric_column(prepared[column])
            )
        )
    ]
    dimension_columns = [
        column
        for column in prepared.columns
        if column not in metric_columns and column not in summary_value_columns
    ]
    if not dimension_columns:
        raise ValueError("Fant ingen dimensjonskolonner i datasettet.")
    if not metric_columns:
        raise ValueError("Fant ingen månedskolonner i datasettet.")

    prepared, dropped_source_summary_rows = _drop_blank_ktoniv7_summary_rows(
        prepared,
        summary_value_columns=summary_value_columns,
        enabled=has_ktoniv7_source,
    )
    if dropped_source_summary_rows:
        adjustments.append(
            {
                "Kategori": "Rensing",
                "Beskrivelse": "Fjernet kilderader uten Ktoniv7-tekst som bare representerte summer.",
                "Verdi": dropped_source_summary_rows,
            }
        )

    dimension_before_fill = prepared[dimension_columns].replace(r"^\s*$", pd.NA, regex=True).copy()
    prepared[dimension_columns] = dimension_before_fill.ffill()

    for column in dimension_columns:
        filled_count = int((dimension_before_fill[column].isna() & prepared[column].notna()).sum())
        if filled_count:
            adjustments.append(
                {
                    "Kategori": "Forward fill",
                    "Beskrivelse": f"Fylte tomme verdier i kolonnen '{column}' nedover.",
                    "Verdi": filled_count,
                }
            )

    first_column_name = prepared.columns[0]
    repeated_first_column_value = _get_repeated_column_value(prepared[first_column_name])
    ktoniv7_column = next((column for column in prepared.columns if "ktoniv7" in column.lower()), None)
    if repeated_first_column_value and ktoniv7_column and ktoniv7_column != first_column_name:
        prepared = prepared.rename(columns={ktoniv7_column: repeated_first_column_value})
        prepared = prepared.drop(columns=[first_column_name])
        prepared.columns = make_unique_column_names(prepared.columns.tolist())
        prepared, dropped_leading_columns_after_remap = _drop_leading_empty_columns(prepared)
        dimension_columns = [
            column
            for column in prepared.columns
            if column not in metric_columns and column not in summary_value_columns
        ]
        adjustments.append(
            {
                "Kategori": "Kolonner",
                "Beskrivelse": "Fjernet første kolonne med gjentatt verdi og brukte teksten som nytt navn for Ktoniv7.",
                "Verdi": f"{first_column_name} -> {repeated_first_column_value}",
            }
        )
        if dropped_leading_columns_after_remap:
            adjustments.append(
                {
                    "Kategori": "Kolonner",
                    "Beskrivelse": "Fjernet tomme kolonner i starten av arket etter Ktoniv7-omdøping.",
                    "Verdi": ", ".join(dropped_leading_columns_after_remap),
                }
            )

    non_numeric_count = 0
    for column in metric_columns + summary_value_columns:
        original_values = prepared[column].copy()
        prepared[column] = prepared[column].map(_coerce_numeric)
        non_numeric_count += int(
            original_values.map(lambda value: normalize_cell(value) != "")
            .where(prepared[column].isna(), False)
            .sum()
        )

    if non_numeric_count:
        adjustments.append(
            {
                "Kategori": "Datatyper",
                "Beskrivelse": "Fant verdier som ikke kunne tolkes som beløp og satte dem til tomme.",
                "Verdi": non_numeric_count,
            }
        )

    columns_to_drop: list[str] = []
    for column in metric_columns:
        if _should_drop_monthly_budget_or_variance(column):
            columns_to_drop.append(column)
        elif _is_regnskap_column(column) and prepared[column].notna().sum() == 0:
            columns_to_drop.append(column)

    if columns_to_drop:
        prepared = prepared.drop(columns=columns_to_drop)

        dropped_budget_or_variance = [
            column for column in columns_to_drop if _should_drop_monthly_budget_or_variance(column)
        ]
        dropped_empty_regnskap = [
            column for column in columns_to_drop if column not in dropped_budget_or_variance
        ]

        if dropped_budget_or_variance:
            adjustments.append(
                {
                    "Kategori": "Kolonner",
                    "Beskrivelse": "Fjernet månedlige kolonner for revidert budsjett eller avvik.",
                    "Verdi": ", ".join(dropped_budget_or_variance),
                }
            )
        if dropped_empty_regnskap:
            adjustments.append(
                {
                    "Kategori": "Kolonner",
                    "Beskrivelse": "Fjernet regnskapskolonner uten tallverdi.",
                    "Verdi": ", ".join(dropped_empty_regnskap),
                }
            )

    remaining_metric_columns = [column for column in metric_columns if column not in columns_to_drop]
    renamed_regnskap_columns: dict[str, str] = {}
    for column in remaining_metric_columns:
        month_name = _get_month_name_for_regnskap_column(column)
        if month_name:
            renamed_regnskap_columns[column] = month_name

    if renamed_regnskap_columns:
        prepared = prepared.rename(columns=renamed_regnskap_columns)
        prepared.columns = make_unique_column_names(prepared.columns.tolist())
        adjustments.append(
            {
                "Kategori": "Kolonner",
                "Beskrivelse": "Endret månedlige regnskapskolonner til månedsnavn.",
                "Verdi": ", ".join(
                    f"{old} -> {new}" for old, new in renamed_regnskap_columns.items()
                ),
            }
        )
    renamed_summary_columns = {
        column: summary_name
        for column in summary_value_columns
        if (summary_name := _get_summary_column_name(column)) is not None
    }
    if renamed_summary_columns:
        prepared = prepared.rename(columns=renamed_summary_columns)
        prepared.columns = make_unique_column_names(prepared.columns.tolist())
        summary_value_columns = [renamed_summary_columns.get(column, column) for column in summary_value_columns]
        adjustments.append(
            {
                "Kategori": "Kolonner",
                "Beskrivelse": "Endret års-/sumkolonner til faste overskrifter.",
                "Verdi": ", ".join(
                    f"{old} -> {new}" for old, new in renamed_summary_columns.items()
                ),
            }
        )
    current_metric_columns = [column for column in prepared.columns if column not in dimension_columns]
    empty_month_columns = [
        column
        for column in current_metric_columns
        if _is_month_column(column) and _is_empty_or_zero_column(prepared[column])
    ]
    if empty_month_columns:
        prepared = prepared.drop(columns=empty_month_columns)
        adjustments.append(
            {
                "Kategori": "Kolonner",
                "Beskrivelse": "Fjernet månedskolonner uten verdi eller kun med 0.",
                "Verdi": ", ".join(empty_month_columns),
            }
        )
        current_metric_columns = [column for column in current_metric_columns if column not in empty_month_columns]

    rows_before_drop = len(prepared)
    prepared = prepared[
        prepared[dimension_columns].notna().any(axis=1) | prepared[current_metric_columns].notna().any(axis=1)
    ].reset_index(drop=True)
    dropped_rows = rows_before_drop - len(prepared)
    if dropped_rows:
        adjustments.append(
            {
                "Kategori": "Rensing",
                "Beskrivelse": "Fjernet helt tomme datarader.",
                "Verdi": dropped_rows,
            }
        )

    prepared, inserted_subtotal_labels = _insert_subtotal_rows(
        prepared,
        current_metric_columns,
        enabled=has_ktoniv7_source,
    )
    if inserted_subtotal_labels:
        adjustments.append(
            {
                "Kategori": "Delsummer",
                "Beskrivelse": "La inn delsumrader basert på første kolonne i arket.",
                "Verdi": ", ".join(inserted_subtotal_labels),
            }
        )
    prepared, total_label = _insert_total_row(
        prepared,
        current_metric_columns,
        subtotal_labels=inserted_subtotal_labels,
        enabled=has_ktoniv7_source,
    )
    if total_label:
        adjustments.append(
            {
                "Kategori": "Totalsum",
                "Beskrivelse": "La inn totalsum på siste rad uten å ta med delsummene.",
                "Verdi": total_label,
            }
        )

    adjustments.extend(
        [
            {
                "Kategori": "Struktur",
                "Beskrivelse": "Beholdt månedskolonner i original venstre-til-høyre-struktur.",
                "Verdi": len(remaining_metric_columns),
            },
            {
                "Kategori": "Struktur",
                "Beskrivelse": "Identifiserte års-/sumkolonner med beløpsverdier.",
                "Verdi": len(summary_value_columns),
            },
            {
                "Kategori": "Struktur",
                "Beskrivelse": "Identifiserte dimensjonskolonner.",
                "Verdi": ", ".join(dimension_columns),
            },
            {
                "Kategori": "Resultat",
                "Beskrivelse": "Antall rader i renset datasett.",
                "Verdi": len(prepared),
            },
        ]
    )

    adjustments_df = pd.DataFrame(adjustments, columns=["Kategori", "Beskrivelse", "Verdi"])
    return CleaningResult(cleaned_df=prepared, adjustments_df=adjustments_df)


def _clean_flat_data_with_report(df: pd.DataFrame) -> CleaningResult:
    prepared = df.copy()
    normalized_columns = [
        normalize_cell(column) or f"Unnamed: {idx}" for idx, column in enumerate(df.columns)
    ]
    prepared.columns = make_unique_column_names(normalized_columns)
    metric_map = {
        column: parsed
        for column in prepared.columns
        if (parsed := _parse_metric_column(column)) is not None
    }

    dimension_columns = [column for column in prepared.columns if column not in metric_map]
    if not dimension_columns:
        raise ValueError("Fant ingen dimensjonskolonner i datasettet.")
    if not metric_map:
        raise ValueError("Fant ingen månedskolonner i datasettet.")

    adjustments: list[dict[str, object]] = []
    prepared["_source_row"] = range(len(prepared))
    dimension_before_fill = prepared[dimension_columns].replace(r"^\s*$", pd.NA, regex=True).copy()
    prepared[dimension_columns] = (
        dimension_before_fill
        .ffill()
    )

    for column in dimension_columns:
        filled_count = int((dimension_before_fill[column].isna() & prepared[column].notna()).sum())
        if filled_count:
            adjustments.append(
                {
                    "Kategori": "Forward fill",
                    "Beskrivelse": f"Fylte tomme verdier i kolonnen '{column}' nedover.",
                    "Verdi": filled_count,
                }
            )

    melted = prepared.melt(
        id_vars=dimension_columns + ["_source_row"],
        value_vars=list(metric_map),
        var_name="Kildefelt",
        value_name="Beløp",
    )

    melted["Måned"] = melted["Kildefelt"].map(lambda column: metric_map[column]["month"])
    melted["Kategori"] = melted["Kildefelt"].map(lambda column: metric_map[column]["category"])
    raw_amounts = melted["Beløp"].copy()
    melted["Beløp"] = melted["Beløp"].map(_coerce_numeric)
    melted["Dato"] = pd.to_datetime(melted["Måned"] + "01", format="%Y%m%d", errors="coerce")
    melted["Kategori"] = pd.Categorical(
        melted["Kategori"],
        categories=CATEGORY_ORDER,
        ordered=True,
    )

    non_numeric_count = int(
        raw_amounts.map(lambda value: normalize_cell(value) != "")
        .where(melted["Beløp"].isna(), False)
        .sum()
    )
    if non_numeric_count:
        adjustments.append(
            {
                "Kategori": "Datatyper",
                "Beskrivelse": "Fant verdier som ikke kunne tolkes som beløp og satte dem til tomme.",
                "Verdi": non_numeric_count,
            }
        )

    rows_before_drop = len(melted)
    melted = melted.dropna(subset=["Beløp"], how="all")
    melted = melted[
        melted[dimension_columns].notna().any(axis=1) | melted["Beløp"].notna()
    ]
    dropped_rows = rows_before_drop - len(melted)
    if dropped_rows:
        adjustments.append(
            {
                "Kategori": "Rensing",
                "Beskrivelse": "Fjernet rader uten beløp etter unpivot.",
                "Verdi": dropped_rows,
            }
        )
    melted = melted.sort_values(
        by=["Kategori", "Måned", "_source_row"],
        kind="stable",
    ).reset_index(drop=True)

    ordered_columns = dimension_columns + ["Måned", "Dato", "Kategori", "Beløp"]
    result = melted[ordered_columns].copy()
    result["Kategori"] = result["Kategori"].astype(str)
    adjustments.extend(
        [
            {
                "Kategori": "Struktur",
                "Beskrivelse": "Identifiserte dimensjonskolonner.",
                "Verdi": ", ".join(dimension_columns),
            },
            {
                "Kategori": "Struktur",
                "Beskrivelse": "Fant månedskolonner for unpivot.",
                "Verdi": len(metric_map),
            },
            {
                "Kategori": "Resultat",
                "Beskrivelse": "Antall rader i renset datasett.",
                "Verdi": len(result),
            },
        ]
    )
    adjustments_df = pd.DataFrame(adjustments, columns=["Kategori", "Beskrivelse", "Verdi"])
    return CleaningResult(cleaned_df=result, adjustments_df=adjustments_df)


def _looks_numeric(value: str) -> bool:
    if not value:
        return False
    cleaned = value.replace(" ", "").replace("\xa0", "")
    cleaned = cleaned.replace(".", "").replace(",", ".")
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", cleaned))


def _parse_metric_column(column_name: str) -> dict[str, str] | None:
    month_match = MONTH_PATTERN.search(column_name)
    if not month_match:
        return None

    month = f"{month_match.group(1)}{month_match.group(2)}"
    lower_name = column_name.lower()
    for keyword, category in CATEGORY_KEYWORDS.items():
        if keyword in lower_name:
            return {"month": month, "category": category}
    return {"month": month, "category": "Ukjent"}


def _should_drop_monthly_budget_or_variance(column_name: str) -> bool:
    lower_name = column_name.lower()
    if not MONTH_PATTERN.search(column_name):
        return False
    return "avvik" in lower_name or ("revidert" in lower_name and "budsjett" in lower_name)


def _is_regnskap_column(column_name: str) -> bool:
    return "regnskap" in column_name.lower()


def _is_summary_value_column(column_name: str) -> bool:
    lower_name = column_name.lower()
    if MONTH_PATTERN.search(column_name):
        return False
    if "som total" in lower_name and any(keyword in lower_name for keyword in CATEGORY_KEYWORDS):
        return True
    if not YEAR_PATTERN.search(column_name):
        return False
    return any(keyword in lower_name for keyword in CATEGORY_KEYWORDS)


def _is_mostly_numeric_column(column: pd.Series, threshold: float = 0.8) -> bool:
    normalized_values = [normalize_cell(value) for value in column.tolist()]
    non_empty_values = [value for value in normalized_values if value]
    if not non_empty_values:
        return False

    numeric_values = [value for value in non_empty_values if _coerce_numeric(value) is not None]
    return (len(numeric_values) / len(non_empty_values)) >= threshold


def _insert_subtotal_rows(
    df: pd.DataFrame,
    value_columns: list[str],
    enabled: bool,
) -> tuple[pd.DataFrame, list[str]]:
    if not enabled or df.empty or not len(df.columns):
        return df, []

    first_column = df.columns[0]
    result = df.copy()
    inserted_labels: list[str] = []

    for rule in SUBTOTAL_RULES:
        matches = result[first_column].map(
            lambda value: any(normalize_cell(value).startswith(prefix) for prefix in rule["prefixes"])
        )
        matching_indices = result.index[matches]
        if matching_indices.empty:
            continue

        subtotal_row = {column: "" for column in result.columns}
        subtotal_row[first_column] = rule["label"]
        for column in value_columns:
            subtotal_row[column] = pd.to_numeric(result.loc[matches, column], errors="coerce").sum(min_count=1)

        insert_at = int(matching_indices[-1]) + 1
        result = pd.concat(
            [
                result.iloc[:insert_at],
                pd.DataFrame([subtotal_row]),
                result.iloc[insert_at:],
            ],
            ignore_index=True,
        )
        inserted_labels.append(rule["label"])

    result.attrs["subtotal_labels"] = inserted_labels
    return result, inserted_labels


def _insert_total_row(
    df: pd.DataFrame,
    value_columns: list[str],
    subtotal_labels: list[str],
    enabled: bool,
) -> tuple[pd.DataFrame, str | None]:
    if not enabled or df.empty or not len(df.columns):
        return df, None

    first_column = df.columns[0]
    total_label = normalize_cell(first_column)
    excluded_labels = set(subtotal_labels)
    detail_rows = ~df[first_column].map(normalize_cell).isin(excluded_labels | {total_label})

    total_row = {column: "" for column in df.columns}
    total_row[first_column] = total_label
    for column in value_columns:
        total_row[column] = pd.to_numeric(df.loc[detail_rows, column], errors="coerce").sum(min_count=1)

    result = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    result.attrs["subtotal_labels"] = subtotal_labels
    result.attrs["total_label"] = total_label
    return result, total_label


def _drop_blank_ktoniv7_summary_rows(
    df: pd.DataFrame,
    summary_value_columns: list[str],
    enabled: bool,
) -> tuple[pd.DataFrame, int]:
    if not enabled or df.empty or not summary_value_columns:
        return df, 0

    ktoniv7_column = next((column for column in df.columns if "ktoniv7" in column.lower()), None)
    if ktoniv7_column is None:
        return df, 0

    blank_ktoniv7 = df[ktoniv7_column].map(normalize_cell).eq("")
    has_summary_values = df[summary_value_columns].apply(
        lambda row: any(normalize_cell(value) != "" for value in row),
        axis=1,
    )
    rows_to_drop = blank_ktoniv7 & has_summary_values
    if not rows_to_drop.any():
        return df, 0

    return df.loc[~rows_to_drop].reset_index(drop=True), int(rows_to_drop.sum())


def _get_month_name_for_regnskap_column(column_name: str) -> str | None:
    if not _is_regnskap_column(column_name):
        return None

    month_match = MONTH_PATTERN.search(column_name)
    if not month_match:
        return None

    return MONTH_NAMES.get(month_match.group(2))


def _get_summary_column_name(column_name: str) -> str | None:
    lower_name = column_name.lower()
    if "regnskap" in lower_name:
        return "Regnskap"
    if "budsjett" in lower_name:
        return "Budsjett"
    if "avvik" in lower_name:
        return "Avvik"
    return None


def _get_repeated_column_value(column: pd.Series) -> str | None:
    normalized_values = [normalize_cell(value) for value in column.tolist()]
    normalized_values = [value for value in normalized_values if value]
    unique_values = list(dict.fromkeys(normalized_values))
    if len(unique_values) == 1:
        return unique_values[0]
    return None


def _is_month_column(column_name: str) -> bool:
    if MONTH_PATTERN.search(column_name):
        return True
    return normalize_cell(column_name).lower() in MONTH_NAMES.values()


def _is_empty_or_zero_column(column: pd.Series) -> bool:
    non_null_values = column.dropna()
    if non_null_values.empty:
        return True
    return bool((non_null_values == 0).all())


def _drop_leading_empty_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    columns_to_drop: list[str] = []
    for column_name in df.columns:
        normalized_values = df[column_name].map(normalize_cell)
        if normalized_values.eq("").all():
            columns_to_drop.append(column_name)
            continue
        break

    if not columns_to_drop:
        return df, []

    return df.drop(columns=columns_to_drop), columns_to_drop


def _coerce_numeric(value: object) -> float | None:
    if pd.isna(value):
        return None
    text = normalize_cell(value)
    if not text:
        return None

    text = text.replace("kr", "").replace("%", "").strip()
    is_negative = False
    if text.startswith("(") and text.endswith(")"):
        is_negative = True
        text = text[1:-1].strip()
    if text.endswith("-"):
        is_negative = True
        text = text[:-1].strip()
    text = re.sub(r"[^0-9,\.\-]", "", text)
    if text.count(",") == 1 and text.count(".") >= 1:
        text = text.replace(".", "").replace(",", ".")
    elif text.count(",") == 1 and text.count(".") == 0:
        text = text.replace(",", ".")
    elif text.count(",") > 1 and text.count(".") == 0:
        text = text.replace(",", "")
    else:
        text = text.replace(",", "")

    try:
        numeric_value = float(text)
    except ValueError:
        return None
    return -abs(numeric_value) if is_negative else numeric_value

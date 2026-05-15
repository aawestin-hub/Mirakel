import calendar
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st
from streamlit_gsheets import GSheetsConnection

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Sandvollen",
    page_icon="🏡",
    layout="wide",
)

BOOKERS = [
    "Alexander",
    "Andreas",
    "Elin",
    "Johanna",
    "Kamilla",
    "Ketil",
    "Konrad",
    "Lukas",
    "Othilie",
    "Sebastian",
    "Victoria",
]
WORKSHEET = "Bookinger"
BOOKING_COLUMNS = ["Booket av", "Fra dato", "Til dato", "Kommentar", "Opprettet"]
MESSAGES_WORKSHEET = "Beskjeder"
MESSAGE_COLUMNS = ["Fra", "Til", "Beskjed", "Opprettet"]
LINKS_WORKSHEET = "Lenker"
LINK_COLUMNS = ["Kategori", "Tittel", "URL"]
HEADER_IMAGE_PATH = BASE_DIR / "assets" / "sandvollen-header.jpg"
WEATHER_LAT = 62.1285
WEATHER_LON = 10.0416
WEATHER_ALTITUDE = 0
WEATHER_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
WEATHER_USER_AGENT = "Sandvollen/1.0"
APP_TIMEZONE = ZoneInfo("Europe/Oslo")

DEFAULT_OFFERS = [
    {
        "butikk": "Joker Folldal",
        "beskrivelse": "Snarvei til kundeavis og lokale tilbud hos Joker.",
        "url": "https://joker.no/",
    },
    {
        "butikk": "Coop Folldal",
        "beskrivelse": "Snarvei til oppdatert kundeavis hos Coop.",
        "url": "https://www.coop.no/minkundeavis",
    },
]

DEFAULT_LINKS = [
    {"Kategori": "Tur og natur", "Tittel": "Nasjonalparkriket", "URL": "https://www.nasjonalparkriket.no/"},
    {"Kategori": "Tur og natur", "Tittel": "UT.no - turforslag i Folldal", "URL": "https://ut.no/utforsker/kommune/1850/folldal"},
    {"Kategori": "Lokal info", "Tittel": "Folldal kommune", "URL": "https://www.folldal.kommune.no/"},
    {"Kategori": "Lokal info", "Tittel": "Visit Norway - Folldal", "URL": "https://www.visitnorway.no/reisemal/ostlandet/fjellnorge/foll-dal/"},
    {"Kategori": "Kart", "Tittel": "Google Maps - Sandvollen", "URL": "https://maps.google.com/?q=Rondeslottbakken+10+Folldal"},
    {"Kategori": "Vær", "Tittel": "Yr - Folldal", "URL": "https://www.yr.no/"},
]

MONTH_NAMES = [
    "Januar",
    "Februar",
    "Mars",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Desember",
]

WEEKDAY_NAMES = ["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"]


def get_secret_value(*keys: str, default=None):
    try:
        value = st.secrets
        for key in keys:
            value = value[key]
        return value
    except Exception:
        return default


def apps_script_is_configured() -> bool:
    return bool(get_secret_value("integrations", "apps_script_url", default=get_secret_value("apps_script_url")))


def get_apps_script_url() -> Optional[str]:
    return get_secret_value("integrations", "apps_script_url", default=get_secret_value("apps_script_url"))


def apps_script_read(url: str, worksheet: str) -> pd.DataFrame:
    response = requests.get(url, params={"action": "read", "worksheet": worksheet}, timeout=20)
    response.raise_for_status()
    payload = response.json()
    rows = payload["rows"] if isinstance(payload, dict) and "rows" in payload else payload
    return pd.DataFrame(rows)


def apps_script_write(url: str, worksheet: str, df: pd.DataFrame) -> None:
    response = requests.post(
        url,
        json={"action": "write", "worksheet": worksheet, "rows": df.fillna("").to_dict(orient="records")},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, dict) and payload.get("status") == "error":
        raise RuntimeError(payload.get("message", "Apps Script write failed"))


def empty_bookings() -> pd.DataFrame:
    return pd.DataFrame(columns=BOOKING_COLUMNS)


def normalize_date_series(values: pd.Series) -> pd.Series:
    return pd.to_datetime(values, errors="coerce", utc=True).dt.tz_convert(APP_TIMEZONE).dt.date


def normalize_bookings(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()

    for column in BOOKING_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = pd.NA

    normalized = normalized[BOOKING_COLUMNS]
    normalized["Booket av"] = normalized["Booket av"].replace({"Meg": "Andreas"})
    normalized["Fra dato"] = normalize_date_series(normalized["Fra dato"])
    normalized["Til dato"] = normalize_date_series(normalized["Til dato"])
    normalized["Opprettet"] = pd.to_datetime(normalized["Opprettet"], errors="coerce")

    normalized = normalized.dropna(subset=["Fra dato", "Til dato"])
    return normalized.sort_values(
        by=["Fra dato", "Til dato", "Booket av"],
        kind="stable",
    ).reset_index(drop=True)


def serialize_bookings(df: pd.DataFrame) -> pd.DataFrame:
    serialized = df.copy()
    serialized["Fra dato"] = pd.to_datetime(serialized["Fra dato"], errors="coerce").dt.strftime("%Y-%m-%d")
    serialized["Til dato"] = pd.to_datetime(serialized["Til dato"], errors="coerce").dt.strftime("%Y-%m-%d")
    serialized["Opprettet"] = pd.to_datetime(serialized["Opprettet"], errors="coerce").dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    return serialized


def load_bookings(conn: Optional[GSheetsConnection], apps_script_url: Optional[str]) -> pd.DataFrame:
    try:
        if conn is not None:
            df = conn.read(worksheet=WORKSHEET, ttl=0)
        elif apps_script_url:
            df = apps_script_read(apps_script_url, WORKSHEET)
        else:
            return empty_bookings()
    except Exception:
        st.error(
            f"Klarte ikke å lese Google Sheet-fanen '{WORKSHEET}'. "
            "Sjekk at arket finnes, og at enten servicekonto eller Apps Script er satt opp riktig."
        )
        st.stop()

    if df is None or df.empty:
        return empty_bookings()

    return normalize_bookings(df)


def save_bookings(conn: Optional[GSheetsConnection], apps_script_url: Optional[str], df: pd.DataFrame) -> None:
    serialized = serialize_bookings(df)
    if conn is not None:
        conn.update(worksheet=WORKSHEET, data=serialized)
        return
    if apps_script_url:
        apps_script_write(apps_script_url, WORKSHEET, serialized)
        return
    raise RuntimeError("No storage backend configured")


def format_date(value: date) -> str:
    return pd.to_datetime(value).strftime("%d.%m.%Y")


def get_conflicts(bookings: pd.DataFrame, from_date: date, to_date: date) -> pd.DataFrame:
    return bookings[
        (bookings["Fra dato"] <= to_date) & (bookings["Til dato"] >= from_date)
    ].reset_index(drop=True)


def booking_nights(from_date: date, to_date: date) -> int:
    return max((to_date - from_date).days, 0) + 1


def add_months(start_year: int, start_month: int, offset: int) -> tuple[int, int]:
    month_index = (start_year * 12 + (start_month - 1)) + offset
    year = month_index // 12
    month = month_index % 12 + 1
    return year, month


def build_booked_day_map(bookings: pd.DataFrame) -> dict[date, set[str]]:
    booked_days: dict[date, set[str]] = {}
    for _, row in bookings.iterrows():
        current = row["Fra dato"]
        end = row["Til dato"]
        booker = row["Booket av"]
        while current <= end:
            booked_days.setdefault(current, set()).add(booker)
            current += timedelta(days=1)
    return booked_days


def render_booking_calendar(
    bookings: pd.DataFrame,
    months_to_show: int = 3,
    show_navigation: bool = True,
    stacked: bool = False,
) -> None:
    st.subheader("Bookingkalender")
    if months_to_show == 3:
        st.markdown(
            "<p class='section-note'>De neste tre månedene vises her. Røde dager betyr at hytta er booket.</p>",
            unsafe_allow_html=True,
        )

    start_offset = 0
    if show_navigation:
        if "calendar_offset" not in st.session_state:
            st.session_state.calendar_offset = 0

        previous_col, label_col, next_col = st.columns([1, 2, 1])
        with previous_col:
            if st.button("← Forrige", use_container_width=True):
                st.session_state.calendar_offset -= 1
        with label_col:
            st.markdown(
                '<p style="text-align:center; color:#6b543c; font-weight:700; margin-top:0.6rem;">'
                "Bla måned for måned"
                "</p>",
                unsafe_allow_html=True,
            )
        with next_col:
            if st.button("Neste →", use_container_width=True):
                st.session_state.calendar_offset += 1

        start_offset = st.session_state.calendar_offset

    booked_day_map = build_booked_day_map(bookings)
    today = date.today()
    start_year, start_month = add_months(today.year, today.month, start_offset)
    month_calendar = calendar.Calendar(firstweekday=0)

    month_blocks = []
    for month_offset in range(months_to_show):
        year, month = add_months(start_year, start_month, month_offset)
        weeks = month_calendar.monthdayscalendar(year, month)
        if len(weeks) < 6:
            weeks.extend([[0] * 7 for _ in range(6 - len(weeks))])

        days_html = "".join(f"<div class='calendar-weekday'>{weekday}</div>" for weekday in WEEKDAY_NAMES)
        for week in weeks:
            for day_number in week:
                if day_number == 0:
                    days_html += "<div class='calendar-day empty'></div>"
                    continue

                current_date = date(year, month, day_number)
                classes = ["calendar-day"]
                if current_date in booked_day_map:
                    classes.append("booked")
                if current_date == today:
                    classes.append("today")

                tooltip = ""
                if current_date in booked_day_map:
                    tooltip = " title='" + ", ".join(sorted(booked_day_map[current_date])) + "'"

                days_html += f"<div class='{' '.join(classes)}'{tooltip}>{day_number}</div>"

        month_blocks.append(
            f'<div class="calendar-month-card">'
            f'<div class="calendar-month-title">{MONTH_NAMES[month - 1]} {year}</div>'
            f'<div class="calendar-grid">{days_html}</div>'
            f"</div>"
        )

    st.markdown(
        "<div class='calendar-container"
        + (" stacked" if stacked else "")
        + "'>"
        + "".join(month_blocks)
        + "</div>",
        unsafe_allow_html=True,
    )


def build_month_overview(bookings: pd.DataFrame) -> pd.DataFrame:
    if bookings.empty:
        return pd.DataFrame(columns=["Måned", "Bookinger", "Netter"])

    overview = bookings.copy()
    overview["Måned"] = pd.to_datetime(overview["Fra dato"]).dt.strftime("%B %Y")
    overview["Netter"] = overview.apply(
        lambda row: booking_nights(row["Fra dato"], row["Til dato"]),
        axis=1,
    )

    return (
        overview.groupby("Måned", sort=False, as_index=False)
        .agg(Bookinger=("Booket av", "count"), Netter=("Netter", "sum"))
        .reset_index(drop=True)
    )


def build_person_summary(bookings: pd.DataFrame) -> pd.DataFrame:
    if bookings.empty:
        return pd.DataFrame(columns=["Person", "Bookinger", "Netter"])

    summary = bookings.copy()
    summary["Netter"] = summary.apply(
        lambda row: booking_nights(row["Fra dato"], row["Til dato"]),
        axis=1,
    )
    return (
        summary.groupby("Booket av", as_index=False)
        .agg(Bookinger=("Booket av", "count"), Netter=("Netter", "sum"))
        .rename(columns={"Booket av": "Person"})
        .sort_values(by=["Bookinger", "Netter", "Person"], ascending=[False, False, True], kind="stable")
        .reset_index(drop=True)
    )


def build_upcoming_overview(bookings: pd.DataFrame) -> pd.DataFrame:
    if bookings.empty:
        return pd.DataFrame(columns=["Booket av", "Fra", "Til", "Netter"])

    upcoming = bookings[bookings["Til dato"] >= date.today()].copy()
    if upcoming.empty:
        return pd.DataFrame(columns=["Booket av", "Fra", "Til", "Netter"])

    upcoming["Fra"] = upcoming["Fra dato"].apply(format_date)
    upcoming["Til"] = upcoming["Til dato"].apply(format_date)
    upcoming["Netter"] = upcoming.apply(
        lambda row: booking_nights(row["Fra dato"], row["Til dato"]),
        axis=1,
    )
    return upcoming[["Booket av", "Fra", "Til", "Netter"]].reset_index(drop=True)


def filter_bookings(bookings: pd.DataFrame, selected_person: str) -> pd.DataFrame:
    if selected_person == "Alle":
        return bookings
    return bookings[bookings["Booket av"] == selected_person].reset_index(drop=True)


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_weather_forecast(lat: float, lon: float, altitude: int) -> dict:
    response = requests.get(
        WEATHER_URL,
        params={"lat": lat, "lon": lon, "altitude": altitude},
        headers={"User-Agent": WEATHER_USER_AGENT},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def build_hourly_weather_table(forecast: dict) -> pd.DataFrame:
    rows = []
    for entry in forecast["properties"]["timeseries"][:12]:
        instant = entry["data"]["instant"]["details"]
        next_hour = entry["data"].get("next_1_hours", {})
        rows.append(
            {
                "Tid": pd.to_datetime(entry["time"]).strftime("%d.%m %H:%M"),
                "Temp": f"{instant['air_temperature']:.0f} °C",
                "Vind": f"{instant['wind_speed']:.0f} m/s",
                "Nedbør": f"{next_hour.get('details', {}).get('precipitation_amount', 0):.1f} mm",
                "Symbol": next_hour.get("summary", {}).get("symbol_code", "ukjent"),
            }
        )
    return pd.DataFrame(rows)


def build_daily_weather_table(forecast: dict) -> pd.DataFrame:
    rows = []
    timeseries = forecast["properties"]["timeseries"]
    for entry in timeseries:
        instant = entry["data"]["instant"]["details"]
        rows.append(
            {
                "Dato": pd.to_datetime(entry["time"]).date(),
                "Temp": instant["air_temperature"],
                "Vind": instant["wind_speed"],
                "Nedbør": entry["data"].get("next_6_hours", {}).get("details", {}).get("precipitation_amount", 0),
            }
        )

    daily = pd.DataFrame(rows)
    if daily.empty:
        return pd.DataFrame(columns=["Dag", "Min", "Maks", "Vind", "Nedbør"])

    daily = (
        daily.groupby("Dato", as_index=False)
        .agg(
            Min=("Temp", "min"),
            Maks=("Temp", "max"),
            Vind=("Vind", "max"),
            Nedbør=("Nedbør", "sum"),
        )
        .head(14)
    )
    daily["Dag"] = daily["Dato"].apply(lambda value: f"{WEEKDAY_NAMES[value.weekday()]} {value.strftime('%d.%m')}")
    daily["Min"] = daily["Min"].map(lambda value: f"{value:.0f} °C")
    daily["Maks"] = daily["Maks"].map(lambda value: f"{value:.0f} °C")
    daily["Vind"] = daily["Vind"].map(lambda value: f"{value:.0f} m/s")
    daily["Nedbør"] = daily["Nedbør"].map(lambda value: f"{value:.1f} mm")
    return daily[["Dag", "Min", "Maks", "Vind", "Nedbør"]]


def empty_messages() -> pd.DataFrame:
    return pd.DataFrame(columns=MESSAGE_COLUMNS)


def normalize_messages(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    for column in MESSAGE_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = pd.NA

    normalized = normalized[MESSAGE_COLUMNS]
    normalized["Opprettet"] = pd.to_datetime(normalized["Opprettet"], errors="coerce")
    normalized = normalized.dropna(subset=["Beskjed"]).fillna("")
    return normalized.sort_values(by="Opprettet", ascending=False, kind="stable").reset_index(drop=True)


def serialize_messages(df: pd.DataFrame) -> pd.DataFrame:
    serialized = df.copy()
    serialized["Opprettet"] = pd.to_datetime(serialized["Opprettet"], errors="coerce").dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    return serialized


def load_messages(conn: Optional[GSheetsConnection], apps_script_url: Optional[str]) -> pd.DataFrame:
    if conn is None and not apps_script_url:
        return empty_messages()

    try:
        if conn is not None:
            df = conn.read(worksheet=MESSAGES_WORKSHEET, ttl=0)
        else:
            df = apps_script_read(apps_script_url, MESSAGES_WORKSHEET)
    except Exception:
        return empty_messages()

    if df is None or df.empty:
        return empty_messages()

    return normalize_messages(df)


def save_messages(conn: Optional[GSheetsConnection], apps_script_url: Optional[str], df: pd.DataFrame) -> None:
    serialized = serialize_messages(df)
    if conn is not None:
        conn.update(worksheet=MESSAGES_WORKSHEET, data=serialized)
        return
    if apps_script_url:
        apps_script_write(apps_script_url, MESSAGES_WORKSHEET, serialized)
        return
    raise RuntimeError("No storage backend configured")


def default_links_df() -> pd.DataFrame:
    return pd.DataFrame(DEFAULT_LINKS)


def normalize_links(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    for column in LINK_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = pd.NA

    normalized = normalized[LINK_COLUMNS].dropna(subset=["Tittel", "URL"]).fillna("")
    return normalized.sort_values(by=["Kategori", "Tittel"], kind="stable").reset_index(drop=True)


def load_links(conn: Optional[GSheetsConnection], apps_script_url: Optional[str]) -> pd.DataFrame:
    if conn is None and not apps_script_url:
        return default_links_df()

    try:
        if conn is not None:
            df = conn.read(worksheet=LINKS_WORKSHEET, ttl=0)
        else:
            df = apps_script_read(apps_script_url, LINKS_WORKSHEET)
    except Exception:
        return default_links_df()

    if df is None or df.empty:
        return default_links_df()

    return normalize_links(df)


def display_header_image() -> None:
    if HEADER_IMAGE_PATH.exists():
        st.image(str(HEADER_IMAGE_PATH), width="stretch")


def apply_custom_styles() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(180deg, #f6f1e7 0%, #fcfaf6 100%);
            }
            .block-container {
                padding-top: 1.4rem;
                padding-bottom: 2.5rem;
                max-width: 1100px;
            }
            .hero-card,
            .info-card {
                background: rgba(255, 252, 247, 0.92);
                border: 1px solid rgba(110, 78, 44, 0.14);
                border-radius: 22px;
                box-shadow: 0 10px 30px rgba(73, 52, 27, 0.08);
            }
            .hero-card {
                padding: 1.4rem 1.5rem;
                margin: 0.6rem 0 1.2rem 0;
            }
            .hero-kicker {
                color: #8a6336;
                font-size: 0.95rem;
                font-weight: 700;
                letter-spacing: 0.04em;
                text-transform: uppercase;
                margin-bottom: 0.4rem;
            }
            .hero-title {
                color: #3d2a18;
                font-size: 2.2rem;
                font-weight: 800;
                line-height: 1.1;
                margin: 0;
            }
            .hero-subtitle {
                color: #6b543c;
                font-size: 1.02rem;
                margin-top: 0.65rem;
                margin-bottom: 0;
            }
            .info-card {
                padding: 1rem 1.1rem;
                margin-bottom: 1rem;
            }
            .page-heading {
                color: #3d2a18;
                font-size: 1.7rem;
                font-weight: 800;
                margin: 0.35rem 0 0.85rem 0;
            }
            .calendar-container {
                display: flex;
                flex-wrap: wrap;
                gap: 1rem;
                margin-bottom: 1.2rem;
            }
            .calendar-container.stacked {
                display: grid;
                grid-template-columns: 1fr;
            }
            .calendar-month-card {
                flex: 1 1 300px;
                min-width: 280px;
                background: rgba(255, 252, 247, 0.92);
                border: 1px solid rgba(110, 78, 44, 0.14);
                border-radius: 22px;
                box-shadow: 0 10px 30px rgba(73, 52, 27, 0.08);
                padding: 1rem;
            }
            .calendar-month-title {
                color: #3d2a18;
                font-size: 1.1rem;
                font-weight: 800;
                margin-bottom: 0.9rem;
            }
            .calendar-grid {
                display: grid;
                grid-template-columns: repeat(7, minmax(0, 1fr));
                gap: 0.35rem;
            }
            .calendar-weekday {
                color: #8a6336;
                font-size: 0.78rem;
                font-weight: 700;
                text-align: center;
            }
            .calendar-day {
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 2.4rem;
                border-radius: 12px;
                background: #f2ede3;
                color: #3d2a18;
                font-weight: 700;
            }
            .calendar-day.empty {
                background: transparent;
            }
            .calendar-day.booked {
                background: #c54848;
                color: white;
            }
            .calendar-day.today {
                outline: 2px solid #8a6336;
                outline-offset: -2px;
            }
            .stat-caption {
                color: #6b543c;
                font-size: 0.92rem;
                margin-top: 0.3rem;
                margin-bottom: 0;
            }
            .info-label {
                color: #8a6336;
                font-size: 0.85rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.04em;
                margin-bottom: 0.2rem;
            }
            .info-value {
                color: #3d2a18;
                font-size: 1.2rem;
                font-weight: 700;
                margin: 0;
            }
            .section-note {
                color: #6b543c;
                margin-top: -0.25rem;
                margin-bottom: 0.9rem;
            }
            .notice-card,
            .link-card,
            .booking-item {
                background: rgba(255, 252, 247, 0.92);
                border: 1px solid rgba(110, 78, 44, 0.14);
                border-radius: 22px;
                box-shadow: 0 10px 30px rgba(73, 52, 27, 0.08);
                padding: 1rem 1.1rem;
                margin-bottom: 0.9rem;
            }
            .booking-item-title {
                color: #3d2a18;
                font-size: 1rem;
                font-weight: 800;
                margin: 0 0 0.25rem 0;
            }
            .booking-item-meta {
                color: #6b543c;
                margin: 0;
                line-height: 1.45;
            }
            .notice-meta {
                color: #8a6336;
                font-size: 0.82rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.04em;
                margin-bottom: 0.45rem;
            }
            .notice-text {
                color: #3d2a18;
                margin: 0;
                line-height: 1.55;
            }
            .link-title {
                color: #3d2a18;
                font-size: 1.05rem;
                font-weight: 800;
                margin: 0 0 0.35rem 0;
            }
            .link-url {
                color: #6b543c;
                font-size: 0.9rem;
                margin: 0;
                word-break: break-word;
            }
            div[data-testid="stForm"] {
                background: rgba(255, 252, 247, 0.92);
                border: 1px solid rgba(110, 78, 44, 0.14);
                border-radius: 22px;
                padding: 1rem 1rem 0.3rem 1rem;
                box-shadow: 0 10px 30px rgba(73, 52, 27, 0.08);
            }
            div[data-testid="stDataFrame"] {
                background: rgba(255, 252, 247, 0.92);
                border-radius: 18px;
                padding: 0.35rem;
                border: 1px solid rgba(110, 78, 44, 0.14);
            }
            div[data-testid="stTabs"] button {
                min-height: 3rem;
                border-radius: 14px 14px 0 0;
                font-weight: 700;
            }
            div[data-baseweb="select"] > div,
            div[data-baseweb="input"] > div {
                min-height: 3.25rem;
                border-radius: 16px;
            }
            .stButton > button,
            div[data-testid="stFormSubmitButton"] > button {
                background: linear-gradient(135deg, #7b5a36 0%, #9a7447 100%);
                color: white;
                border: none;
                border-radius: 999px;
                font-weight: 700;
                min-height: 3.25rem;
            }
            .stButton > button:hover,
            div[data-testid="stFormSubmitButton"] > button:hover {
                background: linear-gradient(135deg, #694b2d 0%, #8a6336 100%);
                color: white;
            }
            @media (max-width: 900px) {
                .hero-title {
                    font-size: 1.8rem;
                }
                .block-container {
                    padding-top: 1rem;
                    padding-bottom: 4rem;
                }
                .hero-card {
                    padding: 1.1rem 1rem;
                }
                .info-card {
                    padding: 0.95rem 1rem;
                }
                .section-note {
                    margin-bottom: 0.75rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def gsheets_is_configured() -> bool:
    try:
        spreadsheet = st.secrets["connections"]["gsheets"]["spreadsheet"]
        return bool(spreadsheet) and "DITT_SHEET_ID" not in spreadsheet
    except Exception:
        return False


def get_connection() -> Optional[GSheetsConnection]:
    if apps_script_is_configured() or not gsheets_is_configured():
        return None
    return st.connection("gsheets", type=GSheetsConnection)


def render_setup_hint() -> None:
    st.warning(
        "Lagring er ikke koblet til ennå. Legg inn enten Google Sheets service account i "
        "`.streamlit/secrets.toml` eller `integrations.apps_script_url` for Apps Script-lagring."
    )


def render_weather_section() -> None:
    try:
        forecast = fetch_weather_forecast(WEATHER_LAT, WEATHER_LON, WEATHER_ALTITUDE)
    except Exception as exc:
        st.error(f"Klarte ikke å hente værdata akkurat nå: {exc}")
        return

    st.dataframe(build_daily_weather_table(forecast), hide_index=True, width="stretch")


def render_webcam_section() -> None:
    st.subheader("Hytta akkurat nå")

    webcam_url = get_secret_value("integrations", "webcam_image_url", default=get_secret_value("webcam_image_url"))
    if not webcam_url:
        st.info("Legg inn `integrations.webcam_image_url` i Secrets når webkamera-bildet er klart.")
        return

    cache_buster = datetime.utcnow().strftime("%Y%m%d%H")
    separator = "&" if "?" in webcam_url else "?"
    st.image(f"{webcam_url}{separator}t={cache_buster}", width="stretch")
    st.caption("Bildet oppdateres med timesbasert cache-busting i appen.")


def render_offers_section() -> None:
    st.subheader("Tilbudsaviser")
    st.markdown(
        '<p class="section-note">Snarveier til ukens tilbud for Joker Folldal og Coop Folldal.</p>',
        unsafe_allow_html=True,
    )

    joker_url = get_secret_value("integrations", "joker_offers_url", default=DEFAULT_OFFERS[0]["url"])
    coop_url = get_secret_value("integrations", "coop_offers_url", default=DEFAULT_OFFERS[1]["url"])

    offers = [
        {**DEFAULT_OFFERS[0], "url": joker_url},
        {**DEFAULT_OFFERS[1], "url": coop_url},
    ]

    for offer in offers:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">{offer['butikk']}</div>
                <p class="hero-subtitle" style="margin-top: 0;">{offer['beskrivelse']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.link_button(f"Åpne {offer['butikk']}", offer["url"], use_container_width=True)


def render_noticeboard(
    conn: Optional[GSheetsConnection], apps_script_url: Optional[str], messages: pd.DataFrame
) -> pd.DataFrame:
    st.subheader("Oppslagsvegg")
    st.markdown(
        '<p class="section-note">Legg igjen en beskjed til nestemann før dere drar fra hytta.</p>',
        unsafe_allow_html=True,
    )

    if conn is None and not apps_script_url:
        st.info("Lagring må være koblet til før oppslagsveggen kan brukes.")
        return messages

    with st.form("noticeboard_form", clear_on_submit=True):
        sender = st.selectbox("Fra", BOOKERS, index=None, placeholder="Velg navn", key="notice_from")
        recipient = st.selectbox("Til", ["Alle", *BOOKERS], key="notice_to")
        message_text = st.text_area("Beskjed", placeholder="F.eks. Vedkurven er fylt opp, men husk å ta med tennbriketter.")
        submitted_notice = st.form_submit_button("Lagre beskjed", width="stretch")

    if submitted_notice:
        if sender is None:
            st.error("Velg hvem beskjeden er fra.")
        elif not message_text.strip():
            st.error("Skriv en beskjed før du lagrer.")
        else:
            new_message = pd.DataFrame(
                [
                    {
                        "Fra": sender,
                        "Til": recipient,
                        "Beskjed": message_text.strip(),
                        "Opprettet": pd.Timestamp.now(),
                    }
                ]
            )
            messages = normalize_messages(pd.concat([messages, new_message], ignore_index=True))
            try:
                save_messages(conn, apps_script_url, messages)
            except Exception as exc:
                st.error(f"Klarte ikke å lagre beskjeden: {exc}")
            else:
                st.success("Beskjeden er lagret.")
                st.rerun()

    if messages.empty:
        st.info("Ingen beskjeder enda.")
    else:
        filter_choice = st.selectbox(
            "Vis beskjeder til",
            ["Alle", *BOOKERS],
            key="notice_filter",
        )
        visible_messages = messages if filter_choice == "Alle" else messages[messages["Til"].isin(["Alle", filter_choice])]

        if visible_messages.empty:
            st.info(f"Ingen beskjeder til {filter_choice} akkurat nå.")
        else:
            for _, row in visible_messages.iterrows():
                created_label = pd.to_datetime(row["Opprettet"]).strftime("%d.%m.%Y %H:%M")
                recipient_label = row["Til"] if row["Til"] else "Alle"
                st.markdown(
                    f"""
                    <div class="notice-card">
                        <div class="notice-meta">{row["Fra"]} → {recipient_label} · {created_label}</div>
                        <p class="notice-text">{row["Beskjed"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    return messages


def render_useful_links(links_df: pd.DataFrame) -> None:
    st.subheader("Nyttige lenker")
    st.markdown(
        '<p class="section-note">Turer, kart og lokal informasjon som er nyttig før og under oppholdet.</p>',
        unsafe_allow_html=True,
    )

    if links_df.empty:
        st.info("Ingen lenker tilgjengelig ennå.")
        return

    for category in links_df["Kategori"].drop_duplicates():
        st.markdown(f"**{category}**")
        category_links = links_df[links_df["Kategori"] == category]
        columns = st.columns(2)
        for index, (_, row) in enumerate(category_links.iterrows()):
            with columns[index % 2]:
                st.markdown(
                    f"""
                    <div class="link-card">
                        <p class="link-title">{row["Tittel"]}</p>
                        <p class="hero-subtitle" style="margin-top: 0;">{category}</p>
                        <p class="link-url">{row["URL"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.link_button(f"Åpne {row['Tittel']}", row["URL"], use_container_width=True)


apply_custom_styles()
display_header_image()
st.markdown("<h1 class='page-heading'>Sandvoll-appen!</h1>", unsafe_allow_html=True)
conn = get_connection()
apps_script_url = get_apps_script_url()
bookings = load_bookings(conn, apps_script_url)
messages = load_messages(conn, apps_script_url)
links_df = load_links(conn, apps_script_url)

page_options = [
    "Book hytta",
    "Se bookinger",
    "Slett booking",
    "Værmelding",
]

valid_page_options = [None, *page_options]
if st.session_state.get("page_selector") not in valid_page_options:
    st.session_state.page_selector = None

if pending_page := st.session_state.pop("next_page_selector", None):
    st.session_state.page_selector = pending_page

selected_page = st.selectbox(
    "hva vil du gjøre",
    valid_page_options,
    key="page_selector",
    format_func=lambda option: "Hva vil du gjøre?" if option is None else option,
    label_visibility="collapsed",
)

if selected_page == "Book hytta":
    with st.form("booking_form", clear_on_submit=True):
        selected_booker = st.selectbox(
            "Hvem booker?",
            BOOKERS,
            index=None,
            placeholder="Velg navn",
        )
        from_date = st.date_input("Fra dato", value=date.today(), format="DD.MM.YYYY")
        to_date = st.date_input("Til dato", value=date.today(), format="DD.MM.YYYY")
        booking_comment = st.text_area("Kommentar", placeholder="Valgfritt")
        submitted = st.form_submit_button("Lagre booking", width="stretch")

    if submitted:
        if conn is None and not apps_script_url:
            st.error("Legg inn enten Google Sheets-oppsett eller Apps Script-URL i Secrets før du lagrer.")
        elif selected_booker is None:
            st.error("Velg et navn før du lagrer bookingen.")
        elif to_date < from_date:
            st.error("Til dato må være lik eller senere enn fra dato.")
        else:
            conflicts = get_conflicts(bookings, from_date, to_date)

            if not conflicts.empty:
                st.warning("Denne perioden overlapper med en eksisterende booking.")
                conflict_table = conflicts[["Booket av", "Fra dato", "Til dato"]].copy()
                conflict_table["Fra dato"] = conflict_table["Fra dato"].apply(format_date)
                conflict_table["Til dato"] = conflict_table["Til dato"].apply(format_date)
                st.dataframe(conflict_table, hide_index=True, width="stretch")
            else:
                success_message = (
                    f"Booking lagret for {selected_booker} fra {format_date(from_date)} til {format_date(to_date)}."
                )
                new_booking = pd.DataFrame(
                    [
                        {
                            "Booket av": selected_booker,
                            "Fra dato": from_date,
                            "Til dato": to_date,
                            "Kommentar": booking_comment.strip(),
                            "Opprettet": pd.Timestamp.now(),
                        }
                    ]
                )

                updated_bookings = normalize_bookings(
                    pd.concat([bookings, new_booking], ignore_index=True)
                )
                save_bookings(conn, apps_script_url, updated_bookings)
                st.session_state.next_page_selector = "Se bookinger"
                st.session_state.booking_success_message = success_message
                st.rerun()

elif selected_page == "Værmelding":
    render_weather_section()

elif selected_page == "Se bookinger":
    if booking_success_message := st.session_state.pop("booking_success_message", None):
        st.success(booking_success_message)
    st.subheader("Eksisterende bookinger")
    if bookings.empty:
        st.info("Ingen bookinger enda.")
    else:
        display_df = bookings[["Booket av", "Fra dato", "Til dato", "Kommentar"]].copy()
        display_df["Fra dato"] = display_df["Fra dato"].apply(format_date)
        display_df["Til dato"] = display_df["Til dato"].apply(format_date)
        display_df["Kommentar"] = display_df["Kommentar"].fillna("").replace("", "—")
        display_df = display_df.rename(columns={"Kommentar": "Kommentarer"})
        st.table(display_df)

    render_booking_calendar(bookings, months_to_show=12, show_navigation=False, stacked=True)

elif selected_page == "Slett booking":
    st.subheader("Slett booking")
    if bookings.empty:
        st.info("Ingen bookinger å slette.")
    else:
        display_df = bookings[["Booket av", "Fra dato", "Til dato", "Kommentar"]].copy()
        display_df["Fra dato"] = display_df["Fra dato"].apply(format_date)
        display_df["Til dato"] = display_df["Til dato"].apply(format_date)
        display_df["Kommentar"] = display_df["Kommentar"].fillna("").replace("", "—")
        display_df = display_df.rename(columns={"Kommentar": "Kommentarer"})
        st.table(display_df)

        with st.form("delete_booking_form"):
            selected_booking_index = st.selectbox(
                "Velg booking som skal slettes",
                bookings.index.tolist(),
                format_func=lambda index: (
                    f"{bookings.loc[index, 'Booket av']} · "
                    f"{format_date(bookings.loc[index, 'Fra dato'])}–{format_date(bookings.loc[index, 'Til dato'])}"
                ),
            )
            delete_submitted = st.form_submit_button("Slett booking", width="stretch")

        if delete_submitted:
            if conn is None and not apps_script_url:
                st.error("Legg inn enten Google Sheets-oppsett eller Apps Script-URL i Secrets før du sletter.")
            else:
                updated_bookings = normalize_bookings(bookings.drop(index=selected_booking_index).reset_index(drop=True))
                save_bookings(conn, apps_script_url, updated_bookings)
                st.success("Bookingen er slettet.")
                st.rerun()

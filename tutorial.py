import streamlit as st
import pandas as pd
import pydeck as pdk

# ===============================
# CONFIG STREAMLIT
# ===============================
st.set_page_config(
    page_title="Mapa logístico",
    layout="wide"
)

st.title("Mapa logístico con filtros")

# ===============================
# CARGA DE DATOS
# ===============================

@st.cache_data
def load_data():
    sharepoint_url = (
        "https://teams.wal-mart.com/:x:/r/sites/ICO0008UpdateBI/Documentos%20compartidos/DashboardMOM/Points_map.csv?d=we32b0f27a3e242fba186b6537d6e1177&csf=1&download=1"
    )

    df = pd.read_csv(sharepoint_url, low_memory=False)

    df.columns = df.columns.str.strip()

    df["CUST_START_TIME"] = pd.to_datetime(df["CUST_START_TIME"])

    df["LATITUDE_DRIVER"] = pd.to_numeric(df["LATITUDE_DRIVER"], errors="coerce")
    df["LONGITUDE_DRIVER"] = pd.to_numeric(df["LONGITUDE_DRIVER"], errors="coerce")

    df = df.dropna(subset=["LATITUDE_DRIVER", "LONGITUDE_DRIVER"])

    return df

df = load_data()

st.write(f"Registros totales: {len(df):,}")

# ===============================
# FILTROS VISUALES
# ===============================
st.sidebar.header("Filtros")

# Fecha
fecha_inicio, fecha_fin = st.sidebar.date_input(
    "Rango de fechas",
    [df["CUST_START_TIME"].min(), df["CUST_START_TIME"].max()]
)

# Store Number
store_number = st.sidebar.multiselect(
    "Store Number",
    sorted(df["STORE_NUMBER"].dropna().unique())
)

# Store Name / Formato
formato = st.sidebar.multiselect(
    "Formato",
    sorted(df["Formato"].dropna().unique())
)

# Estado
edo = st.sidebar.multiselect(
    "Estado",
    sorted(df["edo"].dropna().unique())
)

# Gerente
gerente = st.sidebar.multiselect(
    "Gerente",
    sorted(df["CARRIEL_DLVR"].dropna().unique())
)

# Subgerente
subgerente = st.sidebar.multiselect(
    "Subgerente",
    sorted(df["DRIVER_NAME"].dropna().unique())
)

# ===============================
# APLICAR FILTROS
# ===============================
df_filt = df[
    (df["CUST_START_TIME"].dt.date >= fecha_inicio) &
    (df["CUST_START_TIME"].dt.date <= fecha_fin)
]

if store_number:
    df_filt = df_filt[df_filt["STORE_NUMBER"].isin(store_number)]

if formato:
    df_filt = df_filt[df_filt["Formato"].isin(formato)]

if edo:
    df_filt = df_filt[df_filt["edo"].isin(edo)]

if gerente:
    df_filt = df_filt[df_filt["CARRIEL_DLVR"].isin(gerente)]

if subgerente:
    df_filt = df_filt[df_filt["DRIVER_NAME"].isin(subgerente)]

st.write(f"Registros filtrados: {len(df_filt):,}")

# ===============================
# DATA PARA MAPA
# ===============================
df_map = df_filt.rename(
    columns={
        "LATITUDE_DRIVER": "lat",
        "LONGITUDE_DRIVER": "lon"
    }
)[["lat", "lon"]]

pdk.settings.use_binary_transport = True

# ===============================
# CAPA DE PUNTOS
# ===============================
layer_points = pdk.Layer(
    "ScatterplotLayer",
    data=df_map,
    get_position='[lon, lat]',
    get_radius=12,
    radius_units="pixels",
    get_fill_color=[255, 0, 0, 80],
    pickable=False
)

view_state = pdk.ViewState(
    latitude=float(df_map["lat"].mean()) if len(df_map) else 19.6,
    longitude=float(df_map["lon"].mean()) if len(df_map) else -99.2,
    zoom=9
)

deck = pdk.Deck(
    layers=[layer_points],
    initial_view_state=view_state,
    map_style="light"
)

st.pydeck_chart(deck)


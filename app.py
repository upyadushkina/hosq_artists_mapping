import streamlit as st
import pandas as pd
from pyvis.network import Network
import networkx as nx
import tempfile
import base64

# --- Цветовая схема и параметры ---
PAGE_BG_COLOR = "#262123"
PAGE_TEXT_COLOR = "#E8DED3"
SIDEBAR_BG_COLOR = "#262123"
SIDEBAR_LABEL_COLOR = "#E8DED3"
SIDEBAR_TAG_TEXT_COLOR = "#262123"
SIDEBAR_TAG_BG_COLOR = "#6A50FF"
BUTTON_BG_COLOR = "#262123"
BUTTON_TEXT_COLOR = "#4C4646"
GRAPH_LABEL_COLOR = "#E8DED3"
HEADER_MENU_COLOR = "#262123"

EDGE_COLOR = "#4C4646"
EDGE_OPACITY = 1.0
EDGE_HIGHLIGHT_COLOR = "#6A50FF"
EDGE_HIGHLIGHT_OPACITY = 1.0

GRAPH_WIDTH = "100%"
GRAPH_HEIGHT = "400px"
GRAPH_MARGIN_TOP = "100px"

SOURCE_NODE_COLOR = "#4C4646"

TYPE_COLORS = {
    "Дисциплина": "#6A50FF",
    "Роль": "#975AB2",
    "Стиль": "#B3A0EB",
    "Инструмент": "#EEC0E7",
    "Язык": "#E5B8AB",
    "Опыт": "#D3DAE8",
    "Город": "#B1D3AA",
    "Ищу": "#F4C07C",
    "Куратор": "#EC7F4D",
    "Другое": "#CD5373"
}

# --- Настройки страницы и логотип ---
st.set_page_config(page_title="Граф художников", layout="wide")
logo_path = "logo.png"
if logo_path:
    with open(logo_path, "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <div style="position: absolute; top: 15px; right: 25px;">
            <img src="data:image/png;base64,{logo_data}" width="33">
        </div>
        """,
        unsafe_allow_html=True
    )

# --- CSS стилизация ---
st.markdown(f"""
    <style>
    body, .stApp {{
        background-color: {PAGE_BG_COLOR};
        color: {PAGE_TEXT_COLOR};
    }}
    .stSidebar {{
        background-color: {SIDEBAR_BG_COLOR} !important;
    }}
    .stSidebar label, .stSidebar .css-1n76uvr {{
        color: {SIDEBAR_LABEL_COLOR} !important;
    }}
    .stMultiSelect>div>div {{
        background-color: {PAGE_BG_COLOR} !important;
        color: {PAGE_TEXT_COLOR} !important;
    }}
    .stMultiSelect [data-baseweb="tag"] {{
        background-color: {SIDEBAR_TAG_BG_COLOR} !important;
        color: {SIDEBAR_TAG_TEXT_COLOR} !important;
    }}
    .stButton > button {{
        background-color: {BUTTON_BG_COLOR} !important;
        color: {BUTTON_TEXT_COLOR} !important;
        border: none;
    }}
    header {{
        background-color: {HEADER_MENU_COLOR} !important;
    }}
    iframe {{
        border: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
        margin-top: {GRAPH_MARGIN_TOP};
    }}
    </style>
""", unsafe_allow_html=True)

# --- Загрузка данных ---
def load_data():
    return pd.read_csv("graph_edges.csv")

df = load_data()

# --- Боковая панель с фильтрами ---
st.sidebar.header("Filters")
selected_discipline = st.sidebar.multiselect("Choose disciplines", df[df["type"] == "Дисциплина"]["target"].unique())
selected_role = st.sidebar.multiselect("Choose roles", df[df["type"] == "Роль"]["target"].unique())
selected_style = st.sidebar.multiselect("Choose styles", df[df["type"] == "Стиль"]["target"].unique())
selected_instrument = st.sidebar.multiselect("Choose tools", df[df["type"] == "Инструмент"]["target"].unique())
selected_language = st.sidebar.multiselect("Choose languages of communication", df[df["type"] == "Язык"]["target"].unique())
selected_experience = st.sidebar.multiselect("Choose experiences", df[df["type"] == "Опыт"]["target"].unique())
selected_city = st.sidebar.multiselect("Choose cities", df[df["type"] == "Город"]["target"].unique())
selected_seeking = st.sidebar.multiselect("Choose 'what are you looking for'", df[df["type"] == "Ищу"]["target"].unique())

if st.sidebar.button("Сlean filters"):
    selected_discipline = []
    selected_role = []
    selected_style = []
    selected_instrument = []
    selected_language = []
    selected_experience = []
    selected_city = []
    selected_seeking = []

# --- Фильтрация данных ---
filters = [
    (selected_discipline, "Дисциплина"),
    (selected_role, "Роль"),
    (selected_style, "Стиль"),
    (selected_instrument, "Инструмент"),
    (selected_language, "Язык"),
    (selected_experience, "Опыт"),
    (selected_city, "Город"),
    (selected_seeking, "Ищу")
]

filtered_sources = set(df["source"])
for selected_values, filter_type in filters:
    if selected_values:
        matched_sources = df[(df["type"] == filter_type) & (df["target"].isin(selected_values))]["source"].unique()
        filtered_sources &= set(matched_sources)

if not any(sel for sel, _ in filters):
    filtered_sources = set(df["source"])

filtered_df = df[df["source"].isin(filtered_sources)]

# --- Создаём интерактивный граф с pyvis ---
net = Network(height=GRAPH_HEIGHT, width=GRAPH_WIDTH, bgcolor=PAGE_BG_COLOR, font_color=GRAPH_LABEL_COLOR)

for _, row in filtered_df.iterrows():
    net.add_node(row["source"], label=row["source"], color=SOURCE_NODE_COLOR, size=15)
    net.add_node(row["target"], label=None, title=row["target"], color=TYPE_COLORS.get(row["type"], "#CD5373"), size=10)
    net.add_edge(row["source"], row["target"], color=EDGE_COLOR)

# Включаем физику и взаимодействие
net.set_options("""
var options = {
  edges: {
    color: {
      color: '""" + EDGE_COLOR + """',
      highlight: '""" + EDGE_HIGHLIGHT_COLOR + """',
      opacity: """ + str(EDGE_OPACITY) + """
    },
    width: 1
  },
  interaction: {
    hover: true,
    navigationButtons: true,
    tooltipDelay: 100
  },
  nodes: {
    font: {
      color: '""" + GRAPH_LABEL_COLOR + """'
    }
  },
  physics: {
    enabled: true
  }
}
""")

# --- Сохраняем и отображаем граф ---
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
net.save_graph(temp_file.name)
st.components.v1.html(open(temp_file.name, "r", encoding="utf-8").read(), height=int(GRAPH_HEIGHT.replace("px", "")))

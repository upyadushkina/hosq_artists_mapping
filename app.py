import streamlit as st
import pandas as pd
from pyvis.network import Network
import networkx as nx
import tempfile
import base64

# --- Цветовая схема ---
BACKGROUND_COLOR = "#262123"       # Фон всей страницы
TEXT_COLOR = "#262123"             # Основной цвет текста
SIDEBAR_BG_COLOR = "#E8DED3"       # Фон бокового меню
MULTISELECT_BG_COLOR = "#E8DED3"   # Фон выпадающих списков
MULTISELECT_TAG_COLOR = "#6A50FF"  # Цвет выбранного тега
MULTISELECT_TAG_TEXT = "#E8DED3"   # Цвет текста внутри тега
BUTTON_BG_COLOR = "#262123"        # Фон кнопок
BUTTON_TEXT_COLOR = "#4C4646"       # Текст на кнопках
SOURCE_NODE_COLOR = "#4C4646"       # Цвет узлов-художников

# Цвета узлов по типу
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
st.set_page_config(page_title="Artist Mapping", layout="wide")
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
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
    }}
    .stSidebar {{
        background-color: {SIDEBAR_BG_COLOR} !important;
        color: {TEXT_COLOR} !important;
    }}
    .stMultiSelect>div>div {{
        background-color: {MULTISELECT_BG_COLOR} !important;
        color: {TEXT_COLOR} !important;
    }}
    .stMultiSelect [data-baseweb="tag"] {{
        background-color: {MULTISELECT_TAG_COLOR} !important;
        color: {MULTISELECT_TAG_TEXT} !important;
    }}
    .stButton > button {{
        background-color: {BUTTON_BG_COLOR} !important;
        color: {BUTTON_TEXT_COLOR} !important;
        border: none;
    }}
    iframe {{
        border: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
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

if st.sidebar.button("Сбросить фильтры"):
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
net = Network(height="500px", width="100%", bgcolor=BACKGROUND_COLOR, font_color=TEXT_COLOR)

for _, row in filtered_df.iterrows():
    net.add_node(row["source"], label=row["source"], color=SOURCE_NODE_COLOR, size=15)
    net.add_node(row["target"], label=None, title=row["target"], color=TYPE_COLORS.get(row["type"], "#CD5373"), size=10)
    net.add_edge(row["source"], row["target"], color="#AAAAAA")

net.toggle_physics(True)

# --- Сохраняем и отображаем граф ---
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
net.save_graph(temp_file.name)
st.components.v1.html(open(temp_file.name, "r", encoding="utf-8").read(), height=500)

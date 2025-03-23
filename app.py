import streamlit as st
import pandas as pd
from pyvis.network import Network
import networkx as nx
import tempfile

# --- Стилизация страницы ---
st.set_page_config(page_title="Граф художников", layout="wide")
st.markdown("""
    <style>
    body {
        background-color: #262123;
    }
    .stSidebar {
        background-color: #4C4646;
    }
    .stMultiSelect>div>div {
        background-color: #262123;
        color: #E8DED3;
    }
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #6A50FF !important;
        color: #262123 !important;
    }
    .stSelectbox, .stMultiSelect {
        color: #E8DED3;
    }
    </style>
""", unsafe_allow_html=True)

# Загружаем данные
def load_data():
    return pd.read_csv("graph_edges.csv")

df = load_data()

# Определяем цвета для узлов
source_color = "#4C4646"
type_colors = {
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

# --- Боковая панель с фильтрами ---
st.sidebar.header("🔍 Фильтры")
selected_discipline = st.sidebar.multiselect("Выберите дисциплину", df[df["type"] == "Дисциплина"]["target"].unique())
selected_role = st.sidebar.multiselect("Выберите роль", df[df["type"] == "Роль"]["target"].unique())
selected_style = st.sidebar.multiselect("Выберите стиль", df[df["type"] == "Стиль"]["target"].unique())
selected_instrument = st.sidebar.multiselect("Выберите инструмент", df[df["type"] == "Инструмент"]["target"].unique())
selected_language = st.sidebar.multiselect("Выберите язык общения", df[df["type"] == "Язык"]["target"].unique())
selected_experience = st.sidebar.multiselect("Выберите опыт", df[df["type"] == "Опыт"]["target"].unique())
selected_city = st.sidebar.multiselect("Выберите город", df[df["type"] == "Город"]["target"].unique())
selected_seeking = st.sidebar.multiselect("Выберите 'Ищу'", df[df["type"] == "Ищу"]["target"].unique())

# Кнопка сброса фильтров
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

# Если фильтры пусты — отображаем всех
if not any(sel for sel, _ in filters):
    filtered_sources = set(df["source"])

# Отображаем связи только для подходящих художников
filtered_df = df[df["source"].isin(filtered_sources)]

# --- Создаём интерактивный граф с pyvis ---
net = Network(height="1000px", width="100%", bgcolor="#262123", font_color="white")

for _, row in filtered_df.iterrows():
    net.add_node(row["source"], label=row["source"], color=source_color, size=15)
    net.add_node(row["target"], label=row["target"], color=type_colors.get(row["type"], "#CD5373"), size=10)
    net.add_edge(row["source"], row["target"], color="#AAAAAA")

net.toggle_physics(True)

# Сохраняем и отображаем граф
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
net.save_graph(temp_file.name)
st.components.v1.html(open(temp_file.name, "r", encoding="utf-8").read(), height=1000)

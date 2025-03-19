import streamlit as st
import pandas as pd
from pyvis.network import Network
import networkx as nx
import tempfile

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

# Фильтры
st.sidebar.header("🔍 Фильтры")
selected_discipline = st.sidebar.multiselect("Выберите дисциплину", df[df["type"] == "Дисциплина"]["target"].unique())
selected_role = st.sidebar.multiselect("Выберите роль", df[df["type"] == "Роль"]["target"].unique())
selected_style = st.sidebar.multiselect("Выберите стиль", df[df["type"] == "Стиль"]["target"].unique())
selected_instrument = st.sidebar.multiselect("Выберите инструмент", df[df["type"] == "Инструмент"]["target"].unique())
selected_language = st.sidebar.multiselect("Выберите язык общения", df[df["type"] == "Язык"]["target"].unique())
selected_experience = st.sidebar.multiselect("Выберите опыт", df[df["type"] == "Опыт"]["target"].unique())
selected_city = st.sidebar.multiselect("Выберите город", df[df["type"] == "Город"]["target"].unique())
selected_seeking = st.sidebar.multiselect("Выберите 'Ищу'", df[df["type"] == "Ищу"]["target"].unique())

# Фильтруем данные по выбранным категориям
filtered_df = df.copy()
if selected_discipline:
    filtered_df = filtered_df[filtered_df["target"].isin(selected_discipline)]
if selected_role:
    filtered_df = filtered_df[filtered_df["target"].isin(selected_role)]
if selected_style:
    filtered_df = filtered_df[filtered_df["target"].isin(selected_style)]
if selected_instrument:
    filtered_df = filtered_df[filtered_df["target"].isin(selected_instrument)]
if selected_language:
    filtered_df = filtered_df[filtered_df["target"].isin(selected_language)]
if selected_experience:
    filtered_df = filtered_df[filtered_df["target"].isin(selected_experience)]
if selected_city:
    filtered_df = filtered_df[filtered_df["target"].isin(selected_city)]
if selected_seeking:
    filtered_df = filtered_df[filtered_df["target"].isin(selected_seeking)]

# Создаём интерактивный граф с pyvis
net = Network(height="700px", width="100%", bgcolor="#262123", font_color="white")

# Добавляем узлы и связи
for _, row in filtered_df.iterrows():
    net.add_node(row["source"], label=row["source"], color=source_color, size=15)
    net.add_node(row["target"], label=row["target"], color=type_colors.get(row["type"], "#CD5373"), size=10)
    net.add_edge(row["source"], row["target"], color="#AAAAAA")

# Включаем физику для анимации движения узлов
net.toggle_physics(True)

# Сохраняем граф во временный HTML-файл
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
net.save_graph(temp_file.name)

# Отображаем граф в Streamlit
st.components.v1.html(open(temp_file.name, "r", encoding="utf-8").read(), height=700)

import streamlit as st
import pandas as pd
from pyvis.network import Network
import networkx as nx
import tempfile
import base64
import json

# --- Цветовая схема и параметры ---
PAGE_BG_COLOR = "#262123"              # фон всей страницы
PAGE_TEXT_COLOR = "#E8DED3"            # основной текст на странице
SIDEBAR_BG_COLOR = "#262123"           # фон бокового меню
SIDEBAR_LABEL_COLOR = "#E8DED3"        # подписи к фильтрам
SIDEBAR_TAG_TEXT_COLOR = "#E8DED3"     # текст в выбранных тегах
SIDEBAR_TAG_BG_COLOR = "#6A50FF"       # фон выбранного тега
BUTTON_BG_COLOR = "#262123"            # фон кнопок
BUTTON_TEXT_COLOR = "#E8DED3"          # текст на кнопках
GRAPH_LABEL_COLOR = "#E8DED3"          # цвет подписей узлов графа
HEADER_MENU_COLOR = "#262123"          # цвет верхнего меню Streamlit

EDGE_COLOR = "#4C4646"                  # цвет всех связей
EDGE_OPACITY = 1.0                      # прозрачность связей
EDGE_HIGHLIGHT_COLOR = "#6A50FF"        # цвет связей при наведении
EDGE_HIGHLIGHT_OPACITY = 1.0           # прозрачность активных связей

GRAPH_WIDTH = "100%"                   # ширина окна графа
GRAPH_HEIGHT = "700px"                 # высота окна графа
GRAPH_MARGIN_TOP = "100px"             # отступ сверху для графа

SOURCE_NODE_COLOR = "#4C4646"           # цвет узлов-художников

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
    /* Фикс цвета заголовка Filters */
    section[data-testid="stSidebar"] h1 {{
        color: #E8DED3 !important;
    }}

    /* Цвет стрелочек в multiselect */
    .stMultiSelect svg {{
        fill: #E8DED3 !important;
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
selected_discipline = st.sidebar.multiselect("Choose disciplines", df[df["type"] == "Дисциплина"]["target"].dropna().unique())
selected_role = st.sidebar.multiselect("Choose roles", df[df["type"] == "Роль"]["target"].dropna().unique())
selected_style = st.sidebar.multiselect("Choose styles", df[df["type"] == "Стиль"]["target"].dropna().unique())
selected_instrument = st.sidebar.multiselect("Choose tools", df[df["type"] == "Инструмент"]["target"].dropna().unique())
selected_language = st.sidebar.multiselect("Choose communication languages", df[df["type"] == "Язык"]["target"].dropna().unique())
selected_experience = st.sidebar.multiselect("Choose experience", df[df["type"] == "Опыт"]["target"].dropna().unique())
selected_city = st.sidebar.multiselect("Choose cities", df[df["type"] == "Город"]["target"].dropna().unique())
selected_seeking = st.sidebar.multiselect("Choose 'Seeking'", df[df["type"] == "Ищу"]["target"].dropna().unique())

if st.sidebar.button("Clear filters"):
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
    net.add_node(row["source"], label=None, title=row["source"], color=SOURCE_NODE_COLOR, size=15)
    net.add_node(row["target"], label=None, title=row["target"], color=TYPE_COLORS.get(row["type"], "#CD5373"), size=10)
    net.add_edge(row["source"], row["target"], color=EDGE_COLOR)

# --- JSON-совместимая строка для set_options ---
options_dict = {
    "edges": {
          "color": {
                "color": EDGE_COLOR,                         # основной цвет связи
                "highlight": EDGE_HIGHLIGHT_COLOR,           # цвет связи при наведении/выборе
                "inherit": False,                            # наследовать цвет от узла (True/False)
                "opacity": EDGE_OPACITY                      # прозрачность (0.0 – 1.0)
          },
          "width": 0.5,                                      # толщина линии
          "selectionWidth": 3,                               # толщина при выделении
          "hoverWidth": 1.5,                                 # толщина при наведении
          "smooth": {
                "enabled": True,
                "type": "dynamic"                            # стиль: 'continuous', 'curvedCCW', 'discrete', ...
          }
    },
    "interaction": {
        "hover": True,
        "multiselect": True,              # удерживать Ctrl для выбора нескольких
        "selectable": True,               # позволяет выбирать узлы
        "selectConnectedEdges": True,     # выделять связи выбранных узлов
        "dragNodes": True,
        "dragView": True,
        "zoomView": True,
        "navigationButtons": False,        # стрелки + zoom справа
        "tooltipDelay": 100
    },
    "nodes": {
        "shape": "dot",
        "size": 5,
        "font": {
            "color": GRAPH_LABEL_COLOR,
            "face": "inter",
            # "size": 0
        },
        "opacity": 1
    },
    "manipulation": False,
    "physics": {
        "enabled": False
    },
    "layout": {
        "randomSeed": 42,                  # делает граф стабильным между перезагрузками
        "improvedLayout": True,
        "hierarchical": {
            "enabled": False,
            "levelSeparation": 150,
            "nodeSpacing": 100,
            "treeSpacing": 200,
            "direction": "UD",               # LR, RL, DU
            "sortMethod": "hubsize"
        }
    }
}

net.set_options(json.dumps(options_dict))

# --- Сохраняем и отображаем граф ---
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
net.save_graph(temp_file.name)
st.components.v1.html(open(temp_file.name, "r", encoding="utf-8").read(), height=int(GRAPH_HEIGHT.replace("px", "")))

import streamlit as st
st.cache_data.clear()

import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

# Загружаем данные
@st.cache_data
def load_data():
    return pd.read_csv("HOSQ_artists.csv")

df = load_data()

# Заголовок приложения
st.title("🎨 Сеть связей художников")

# Фильтры в боковой панели
st.sidebar.header("🔍 Фильтр")
selected_style = st.sidebar.multiselect("Выберите стиль", df["Стиль"].dropna().unique())
selected_language = st.sidebar.multiselect("Выберите язык общения", df["Язык общения"].dropna().unique())

# Фильтруем данные
filtered_df = df.copy()
if selected_style:
    filtered_df = filtered_df[df["Стиль"].str.contains("|".join(selected_style), na=False)]
if selected_language:
    filtered_df = filtered_df[df["Язык общения"].str.contains("|".join(selected_language), na=False)]

# Создаём граф
G = nx.Graph()
for _, row in filtered_df.iterrows():
    G.add_node(row["Имя"], group="Художник")
    for style in row["Стиль"].split(", "):
        G.add_node(style, group="Стиль")
        G.add_edge(row["Имя"], style)
    for language in row["Язык общения"].split(", "):
        G.add_node(language, group="Язык общения")
        G.add_edge(row["Имя"], language)

# Координаты узлов
pos = nx.spring_layout(G, seed=42)

# Создаём связи (рёбра)
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=1, color="#888"),
    hoverinfo='none',
    mode='lines'
)

# Узлы (вершины)
node_x = []
node_y = []
node_labels = []
node_colors = []

# Цвета категорий
category_colors = {
    "Художник": "#E8DED3",
    "Стиль": "#EC7F4D",
    "Язык общения": "#E5B8AB"
}

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_labels.append(str(node))
    node_colors.append(category_colors.get(G.nodes[node].get("group", ""), "#000000"))

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    text=node_labels,
    marker=dict(size=10, color=node_colors),
    textposition="top center"
)

# Отображаем граф
fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title="Граф связей художников",
                    showlegend=False,
                    hovermode='closest'
                ))

st.plotly_chart(fig)

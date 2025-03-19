import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

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
selected_types = st.sidebar.multiselect("Выберите типы связей", df["type"].unique(), df["type"].unique())

# Фильтруем данные по выбранным типам
df_filtered = df[df["type"].isin(selected_types)]

# Создаём граф
G = nx.Graph()
for _, row in df_filtered.iterrows():
    G.add_node(row["source"], group="source", color=source_color)
    G.add_node(row["target"], group=row["type"], color=type_colors.get(row["type"], "#CD5373"))
    G.add_edge(row["source"], row["target"])

# Расположение узлов
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

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_labels.append(str(node))
    node_colors.append(G.nodes[node]["color"])

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
                    hovermode='closest',
                    plot_bgcolor='#262123',
                    paper_bgcolor='#262123',
                    xaxis=dict(showgrid=False, zeroline=False, visible=False),
                    yaxis=dict(showgrid=False, zeroline=False, visible=False)
                ))

st.plotly_chart(fig)

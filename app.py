import streamlit as st
import anthropic
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import plotly.graph_objects as go

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model = SentenceTransformer('all-MiniLM-L6-v2')

st.set_page_config(page_title="chaos organizer", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, .stApp {
    background-color: #fdf4f2;
    font-family: 'Inter', sans-serif;
}
.stTextArea textarea {
    background-color: #ffffff;
    color: #2d2424;
    border: none;
    border-radius: 20px;
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    padding: 20px;
}
.stButton button {
    background-color: #2d2424;
    color: #ffffff;
    border: none;
    border-radius: 999px;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 500;
}
.stButton button:hover {
    background-color: #4a3d3d;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def cluster_ideas(ideas, embeddings):
    clusters = []
    assigned = set()
    for i in range(len(ideas)):
        if i in assigned:
            continue
        cluster = [ideas[i]]
        assigned.add(i)
        for j in range(i + 1, len(ideas)):
            if j not in assigned:
                sim = cosine_similarity(embeddings[i], embeddings[j])
                if sim > 0.4:
                    cluster.append(ideas[j])
                    assigned.add(j)
        clusters.append(cluster)
    return clusters

def create_graph(ideas, embeddings, clusters):
    idea_to_cluster = {}
    for i, cluster in enumerate(clusters):
        for idea in cluster:
            idea_to_cluster[idea] = i

    colors = ['#c9a89a', '#a8c9b8', '#a8b8c9', '#c9bda8', '#b8a8c9', '#c9c3a8', '#c9a8b8']

    n = len(ideas)
    angles = [2 * np.pi * i / n for i in range(n)]

    x_pos, y_pos = [], []
    for i in range(n):
        cluster_idx = idea_to_cluster[ideas[i]]
        cluster_angle = 2 * np.pi * cluster_idx / max(len(clusters), 1)
        angle = 0.6 * cluster_angle + 0.4 * angles[i]
        radius = 1 + 0.3 * (i % 3)
        x_pos.append(radius * np.cos(angle))
        y_pos.append(radius * np.sin(angle))

    fig = go.Figure()

    for i in range(n):
        for j in range(i + 1, n):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            if sim > 0.4:
                cluster_idx = idea_to_cluster[ideas[i]]
                color = colors[cluster_idx % len(colors)]
                fig.add_trace(go.Scatter(
                    x=[x_pos[i], x_pos[j], None],
                    y=[y_pos[i], y_pos[j], None],
                    mode='lines',
                    line=dict(width=sim * 2, color=color.replace('#', 'rgba(').replace(')', f',{sim * 0.4})')),
                    showlegend=False,
                    hoverinfo='none'
                ))

    for i, idea in enumerate(ideas):
        cluster_idx = idea_to_cluster[idea]
        color = colors[cluster_idx % len(colors)]
        fig.add_trace(go.Scatter(
            x=[x_pos[i]],
            y=[y_pos[i]],
            mode='markers+text',
            marker=dict(size=14, color=color),
            text=[idea],
            textposition='top center',
            textfont=dict(color='#2d2424', size=12, family='Inter'),
            showlegend=False,
            hovertext=idea,
            hoverinfo='text'
        ))

    fig.update_layout(
        paper_bgcolor='#fdf4f2',
        plot_bgcolor='#fdf4f2',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=20, r=20, t=20, b=20),
        height=480
    )
    return fig

def get_priorities(clusters):
    clusters_text = ""
    for i, cluster in enumerate(clusters):
        clusters_text += f"Group {i+1}: {', '.join(cluster)}\n"
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": f"""These are someone's ideas grouped by topic:

{clusters_text}

Give me:
1. A short name for each group (2-3 words max, lowercase)
2. Top 3 priorities, one line each, no fluff
3. One honest sentence summarizing what's going on

Be direct. No emojis. No corporate language."""}]
    )
    return message.content[0].text

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='margin-bottom: 40px;'>
    <p style='font-size: 40px; font-weight: 700; color: #2d2424; letter-spacing: -0.5px; margin: 0; line-height: 1.2;'>chaos organizer</p>
    <p style='font-size: 17px; color: #9c8a87; font-weight: 400; margin: 8px 0 0 0;'>what's cluttering your mind right now?</p>
</div>
""", unsafe_allow_html=True)

brain_dump = st.text_area(
    "",
    height=140,
    placeholder="paste anything — notes, tasks, ideas, thoughts. one per line or comma separated.",
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)
col_btn, _ = st.columns([1, 4])
with col_btn:
    organize = st.button("organize →")

if organize and brain_dump.strip():
    if "," in brain_dump:
        ideas = [i.strip() for i in brain_dump.split(",") if i.strip()]
    else:
        ideas = [i.strip() for i in brain_dump.split("\n") if i.strip()]

    with st.spinner("thinking..."):
        embeddings = model.encode(ideas)
        clusters = cluster_ideas(ideas, embeddings)
        priorities = get_priorities(clusters)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("<p style='font-size: 12px; font-weight: 600; color: #9c8a87; letter-spacing: 1.5px; text-transform: uppercase;'>idea map</p>", unsafe_allow_html=True)
        fig = create_graph(ideas, embeddings, clusters)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<p style='font-size: 12px; font-weight: 600; color: #9c8a87; letter-spacing: 1.5px; text-transform: uppercase;'>structure</p>", unsafe_allow_html=True)
        st.markdown(f"<div style='color: #2d2424; font-size: 15px; line-height: 2;'>{priorities.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
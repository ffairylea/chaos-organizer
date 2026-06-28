import streamlit as st
import anthropic
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model = SentenceTransformer('all-MiniLM-L6-v2')

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def cluster_ideas(ideas):
    embeddings = model.encode(ideas)
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

def organize_with_claude(clusters):
    clusters_text = ""
    for i, cluster in enumerate(clusters):
        clusters_text += f"Group {i+1}: {', '.join(cluster)}\n"
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"""Here are ideas grouped by similarity:

{clusters_text}

Please:
1. Give each group a clear name
2. Pick the top 3 priorities
3. Write a one-line summary"""}]
    )
    return message.content[0].text

st.title("chaos organizer")
st.write("paste your messy thoughts below, one per line or comma separated")

brain_dump = st.text_area("your brain dump", height=200, placeholder="art history essay, SAT prep, call mum, chemistry notes...")

if st.button("organize my chaos"):
    if brain_dump:
        with st.spinner("clustering your ideas..."):
            if "," in brain_dump:
                ideas = [i.strip() for i in brain_dump.split(",")]
            else:
                ideas = [i.strip() for i in brain_dump.split("\n") if i.strip()]
            
            clusters = cluster_ideas(ideas)
            result = organize_with_claude(clusters)

        st.subheader("your organized brain")
        st.markdown(result)

        st.subheader("idea clusters")
        for i, cluster in enumerate(clusters):
            with st.expander(f"group {i+1} ({len(cluster)} ideas)"):
                for idea in cluster:
                    st.write(f"• {idea}")
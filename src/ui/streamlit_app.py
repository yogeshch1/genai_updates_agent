# src/ui/streamlit_app.py
from pathlib import Path
import sys
import streamlit as st
import pandas as pd
import sqlalchemy as sa

# make src/ importable
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from db.models import get_engine

st.set_page_config(page_title="GenAI Agent — Items", layout="wide")
st.title("GenAI Agent — Latest Items")

engine = get_engine()

with st.spinner("Loading latest items..."):
    query = "SELECT id, source, source_id, title, published_date, url FROM items ORDER BY published_date DESC NULLS LAST LIMIT 200;"
    with engine.connect() as conn:
        result = conn.execute(sa.text(query))
        rows = result.fetchall()
        df = pd.DataFrame(rows, columns=result.keys())

if df.empty:
    st.info("No items yet — run the arXiv fetcher (`python src/fetchers/arxiv_fetcher.py --once`) to populate the DB.")
else:
    # Show table and simple clickable list
    st.dataframe(df[["source", "title", "published_date"]], height=300)

    st.markdown("### Quick links")
    for _, r in df.iterrows():
        title = r["title"]
        url = r["url"] or ""
        source = r["source"]
        pub = r["published_date"]
        if pd.isna(pub):
            pub = ""
        st.markdown(f"- **{source}** — [{title}]({url}) — {pub}")

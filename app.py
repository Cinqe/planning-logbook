from datetime import datetime
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Planning Unit Logbook", page_icon="📂", layout="centered"
)

# Custom CSS to mimic a clean desktop-like card padding and borders
st.markdown(
    """
    <style>
    .log-card {
        background-color: #161b22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("📂 Planning Unit Logbook")
st.caption("Mobile Viewer Interface")

# Connect to database and load fresh data without caching
conn = sqlite3.connect("logbook.db")


def load_data():
  return pd.read_sql_query("SELECT * FROM logs ORDER BY id DESC", conn)


df = load_data()
conn.close()

if df.empty:
  st.warning("No logs found in your database.")
else:
  # Filter controls side-by-side
  col1, col2 = st.columns(2)
  with col1:
    category_filter = st.selectbox(
        "Category", ["All", "Received", "Released"]
    )
  with col2:
    search_query = st.text_input("🔍 Search", placeholder="Subject/Sender...")

  if category_filter != "All":
    df = df[df["category"] == category_filter]

  if search_query:
    df = df[
        df["subject"].str.contains(search_query, case=False, na=False)
        | df["sender_or_destination"].str.contains(
            search_query, case=False, na=False
        )
        | df["doc_type"].str.contains(search_query, case=False, na=False)
    ]

  st.markdown(f"--- \n **Total Records Found: {len(df)}**")

  # Render records in card containers
  for _, row in df.iterrows():
    badge = "🟢 Received" if row["category"] == "Received" else "🔵 Released"
    with st.container():
      st.markdown(
          f"""
            <div style="background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 12px;">
                <span style="font-size: 0.85rem; color: #8b949e;">{row['date_logged']} | <b>{row['series']}</b></span>
                <h4 style="margin: 5px 0; color: #58a6ff;">{row['subject']}</h4>
                <p style="margin: 2px 0; font-size: 0.9rem;"><b>Type:</b> {row['doc_type']} &nbsp;|&nbsp; <b>{badge}</b></p>
                <p style="margin: 2px 0; font-size: 0.9rem;"><b>Sender/Destination:</b> {row['sender_or_destination']}</p>
                {f'<p style="margin-top: 5px; font-size: 0.85rem; color: #8b949e;"><i>Remarks: {row["remarks"]}</i></p>' if row["remarks"] else ''}
            </div>
            """,
          unsafe_allow_html=True,
      )
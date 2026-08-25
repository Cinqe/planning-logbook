import os
import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="Planning Unit Logbook", page_icon="📋", layout="centered"
)

# Initialize Supabase connection using Streamlit secrets (or direct strings for testing)
SUPABASE_URL = st.secrets.get(
    "SUPABASE_URL", "https://riinxzuilloipkoqlyvv.supabase.co"
)
SUPABASE_KEY = st.secrets.get(
    "SUPABASE_KEY", "sb_publishable_u7paOZQo5tEG3ICXY1yV7g_UB2ceW5e"
)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Scaled down further to fit nicely on a single line in mobile view
st.markdown(
    """
    <h3 style="margin: 0px 0px 5px 0px; font-size: 1.25rem; display: flex; align-items: center; gap: 8px;">
        📋 Planning Unit Logbook
    </h3>
""",
    unsafe_allow_html=True,
)
st.caption("Live Cloud Mobile Viewer")


# Fetch data directly from Supabase cloud database
def load_data():
  response = (
      supabase.table("logs").select("*").order("id", desc=True).execute()
  )
  return pd.DataFrame(response.data)


# ==========================================
# ATTACHMENT PREVIEW COMPONENT FOR STREAMLIT
# ==========================================
def render_attachment_preview(attachment_url):
  if not attachment_url or str(attachment_url).strip() == "":
    st.info("No attachment available for this entry.")
    return

  st.markdown("---")
  st.markdown("**📎 Document Attachment:**")

  clean_url = str(attachment_url).split("?")[0].lower()

  # 1. Image Previews (.jpg, .jpeg, .png, .webp, .gif)
  if clean_url.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
    st.image(attachment_url, caption="Attached Image", use_container_width=True)

  # 2. PDFs and Other Documents
  else:
    file_name = os.path.basename(clean_url)
    st.markdown(f"📄 **File:** `{file_name}`")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
      # Opens file safely in a new browser tab
      st.markdown(
          f"""
                <a href="{attachment_url}" target="_blank" style="display:inline-block;padding:10px 16px;background-color:#5865F2;color:white;text-align:center;font-weight:bold;text-decoration:none;border-radius:6px;width:100%;">
                    🔍 Open / Read File
                </a>
                """,
          unsafe_allow_html=True,
      )
    with col_btn2:
      # Forces download
      st.markdown(
          f"""
                <a href="{attachment_url}" download style="display:inline-block;padding:10px 16px;background-color:#248046;color:white;text-align:center;font-weight:bold;text-decoration:none;border-radius:6px;width:100%;">
                    📥 Download File
                </a>
                """,
          unsafe_allow_html=True,
      )


df = load_data()

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
    badge = "📥 Received" if row["category"] == "Received" else "📤 Released"
    with st.container():
      st.markdown(
          f"""
            <div style="background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px;">
                <span style="font-size: 0.85rem; color: #8b949e;">{row['date_logged']} | <b>{row['series']}</b></span>
                <h4 style="margin: 5px 0; color: #58a6ff;">{row['subject']}</h4>
                <p style="margin: 2px 0; font-size: 0.9rem;"><b>Type:</b> {row['doc_type']} &nbsp;|&nbsp; <b>{badge}</b></p>
                <p style="margin: 2px 0; font-size: 0.9rem;"><b>Sender/Destination:</b> {row['sender_or_destination']}</p>
                {f'<p style="margin-top: 5px; font-size: 0.85rem; color: #8b949e;"><i>Remarks: {row["remarks"]}</i></p>' if row.get("remarks") else ''}
            </div>
            """,
          unsafe_allow_html=True,
      )

      # Expander to view details and use the new attachment action buttons
      with st.expander("👁️ View Attachment / Details"):
        st.write(
            f"**Office/Destination:** {row.get('office_destination', 'N/A')}"
        )
        render_attachment_preview(row.get("attachment_path"))

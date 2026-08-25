import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_pdf_viewer import pdf_viewer
from supabase import create_client

st.set_page_config(
    page_title="Planning Unit Logbook", page_icon="📋", layout="centered"
)

# Automatically refresh and pull from Supabase every 10 seconds (10000 milliseconds)
st_autorefresh(interval=10000, key="logbook_auto_refresher")

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
def render_attachment_preview(attachment_url, row_id):
  if not attachment_url or str(attachment_url).strip() == "":
    st.info("No attachment available for this entry.")
    return

  st.markdown("---")
  st.markdown("**📎 Document Preview & Download:**")

  clean_url = str(attachment_url).split("?")[0].lower()
  file_name = os.path.basename(clean_url)
  if not file_name:
    file_name = "document.pdf"

  # 1. Image Previews (.jpg, .jpeg, .png, .webp, .gif)
  if clean_url.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
    st.image(attachment_url, caption="Attached Image", use_container_width=True)

  # 2. PDF Document Preview with Page Navigation Controls
  elif clean_url.endswith(".pdf"):
    st.markdown(f"📄 **File:** `{file_name}`")
    try:
      import fitz  # PyMuPDF to count total pages dynamically
      import urllib.request

      with urllib.request.urlopen(attachment_url) as response:
        pdf_bytes = response.read()

      # Open PDF with PyMuPDF to get total page count
      doc = fitz.open(stream=pdf_bytes, filetype="pdf")
      total_pages = len(doc)

      # Initialize unique session state for this specific row's page tracker
      page_key = f"current_page_{row_id}"
      if page_key not in st.session_state:
        st.session_state[page_key] = 1

      # Ensure page bounds are safe
      if st.session_state[page_key] > total_pages:
        st.session_state[page_key] = total_pages
      if st.session_state[page_key] < 1:
        st.session_state[page_key] = 1

      current_page = st.session_state[page_key]

      # Render only the single active page responsively
      pdf_viewer(input=pdf_bytes, pages_to_render=[current_page])

      # Navigation control bar if there's more than 1 page
      if total_pages > 1:
        st.markdown("")
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])

        with nav_col1:
          if st.button(
              "◀ Prev",
              key=f"prev_{row_id}",
              disabled=(current_page <= 1),
              use_container_width=True,
          ):
            st.session_state[page_key] -= 1
            st.rerun()

        with nav_col2:
          st.markdown(
              f"<p style='text-align:center; margin: 5px 0; font-size: 0.9rem;'>Page <b>{current_page}</b> of <b>{total_pages}</b></p>",
              unsafe_allow_html=True,
          )

        with nav_col3:
          if st.button(
              "Next ▶",
              key=f"next_{row_id}",
              disabled=(current_page >= total_pages),
              use_container_width=True,
          ):
            st.session_state[page_key] += 1
            st.rerun()

    except Exception as e:
      st.error(f"Could not load visual preview: {e}")

  # 3. Other File Types (Fallback)
  else:
    st.markdown(f"📄 **File:** `{file_name}`")

  # Force download parameter for the download button
  separator = "&" if "?" in attachment_url else "?"
  force_download_url = f"{attachment_url}{separator}download={file_name}"

  # Clean download action button below preview
  st.markdown(
      f"""
        <a href="{force_download_url}" style="display:block;padding:10px 16px;background-color:#248046;color:white;text-align:center;font-weight:bold;text-decoration:none;border-radius:6px;width:100%;margin-top:10px;">
            📥 Download File
        </a>
        """,
      unsafe_allow_html=True,
  )


# Quick update control row
col_top1, col_top2 = st.columns([3, 1])
with col_top2:
  if st.button("🔄 Check Updates"):
    st.rerun()

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

      # Expander to view details and render page-by-page PDF viewer
      with st.expander("👁️ View Attachment / Details"):
        st.write(
            f"**Office/Destination:** {row.get('office_destination', 'N/A')}"
        )
        render_attachment_preview(row.get("attachment_path"), row["id"])

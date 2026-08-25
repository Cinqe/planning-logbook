import streamlit as st
import os

# ==========================================
# ATTACHMENT PREVIEW COMPONENT FOR STREAMLIT
# ==========================================
def render_attachment_preview(attachment_url):
    if not attachment_url:
        st.info("No attachment available for this entry.")
        return

    st.markdown("---")
    st.subheader("📎 Attachment Preview")
    
    # Clean URL parameters if any exist from Supabase public URL
    clean_url = attachment_url.split("?")[0].lower()
    
    # 1. Image Previews (.jpg, .jpeg, .png, .webp)
    if clean_url.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
        st.image(attachment_url, caption="Attached Image", use_column_width=True)
        
    # 2. PDF Document Previews (.pdf)
    elif clean_url.endswith('.pdf'):
        st.markdown(f"**PDF Document Detected:** [Open in New Tab]({attachment_url})")
        # Embed PDF using HTML iframe
        pdf_display = f'<iframe src="{attachment_url}" width="100%" height="600px" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        
    # 3. Audio Files (.mp3, .wav)
    elif clean_url.endswith(('.mp3', '.wav', '.ogg')):
        st.audio(attachment_url)
        
    # 4. Video Files (.mp4, .mov)
    elif clean_url.endswith(('.mp4', '.mov', '.webm')):
        st.video(attachment_url)
        
    # 5. Other Files (Word documents, spreadsheets, etc.)
    else:
        st.warning("Direct inline preview is not supported for this file type.")
        st.markdown(f"📥 [Click here to download/view the file]({attachment_url})", unsafe_allow_html=True)

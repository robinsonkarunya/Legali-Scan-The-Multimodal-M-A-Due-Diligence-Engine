import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image

# 1. Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 2. Page Configuration
st.set_page_config(page_title="Legali-Scan AI", page_icon="⚖️", layout="wide")
st.title("⚖️ Legali-Scan: M&A Due Diligence Engine")
st.markdown("### *Multimodal Deep-Audit for Industrial & Corporate Mergers*")

# 3. Sidebar for Uploads
with st.sidebar:
    st.header("Data Room Upload")
    uploaded_files = st.file_uploader(
        "Upload Contracts (PDF) or Site Plans (Images)", 
        type=["pdf", "jpg", "jpeg", "png"], 
        accept_multiple_files=True
    )
    audit_button = st.button("🔍 Start Deep Audit")

# 4. Main Interface Logic
if audit_button and uploaded_files:
    with st.spinner("Gemini is analyzing the data room..."):
        try:
            # Prepare contents for Gemini
            model_inputs = []
            
            # Instruction for the AI
            instruction = """
            You are a Senior M&A Legal Auditor. Analyze the provided documents as a single 'Data Room'.
            1. Find conflicting clauses (e.g., Change of Control terms).
            2. Match visual evidence (images) with text descriptions in contracts.
            3. Highlight 'Invisible Risks' like handwritten notes or missing signatures.
            4. Provide a 'Liability Heatmap' and cite page numbers/file names.
            """
            model_inputs.append(instruction)

            # Process files for Gemini API
            for uploaded_file in uploaded_files:
                if uploaded_file.type == "application/pdf":
                    # Use Gemini's File API for PDFs (Long Context)
                    # For a hackathon, we temporarily save to send to API
                    with open(uploaded_file.name, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    genai_file = genai.upload_file(path=uploaded_file.name)
                    model_inputs.append(genai_file)
                else:
                    # Process images directly
                    img = Image.open(uploaded_file)
                    model_inputs.append(img)

            # 5. Call Gemini 1.5 Pro
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(model_inputs)
            
            # Display Result
            st.success("Audit Complete!")
            st.markdown("---")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Error: {e}")

elif not uploaded_files:
    st.info("Please upload files in the sidebar to begin.")
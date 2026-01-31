import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
from fpdf import FPDF

# --- 1. PDF GENERATOR FUNCTION ---
def create_pdf(report_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    # Ensure text is compatible with basic PDF encoding
    cleaned_text = report_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=cleaned_text)
    return pdf.output()

# --- 2. CONFIG & API SETUP ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

st.set_page_config(page_title="Legali-Scan AI", page_icon="⚖️", layout="wide")
st.title("⚖️ Legali-Scan: M&A Due Diligence Engine")
st.markdown("### *Multimodal Deep-Audit for Industrial & Corporate Mergers*")

# --- 3. SIDEBAR UPLOAD ---
with st.sidebar:
    st.header("Data Room Upload")
    uploaded_files = st.file_uploader(
        "Upload Contracts (PDF) or Site Plans (Images)", 
        type=["pdf", "jpg", "jpeg", "png"], 
        accept_multiple_files=True
    )
    audit_button = st.button("🔍 Start Deep Audit")

# --- 4. AUDIT LOGIC ---
if audit_button and uploaded_files:
    with st.spinner("Gemini is auditing the data room..."):
        try:
            model_inputs = []
            
            # The Winning Prompt
            instruction = """
            You are a Senior M&A Legal Auditor. Analyze the provided documents as a single 'Data Room'.
            1. Find conflicting clauses (e.g., Change of Control terms).
            2. Match visual evidence (images) with text descriptions in contracts.
            3. Highlight 'Invisible Risks' like handwritten notes or missing signatures.
            4. Provide a 'Liability Heatmap' and cite page numbers/file names.
            """
            model_inputs.append(instruction)

            # Process Files
            for uploaded_file in uploaded_files:
                if uploaded_file.type == "application/pdf":
                    # Save temporarily to upload to Gemini File API
                    with open(uploaded_file.name, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    genai_file = genai.upload_file(path=uploaded_file.name)
                    model_inputs.append(genai_file)
                else:
                    img = Image.open(uploaded_file)
                    model_inputs.append(img)

            # Call the Model (Gemini 3 Flash for speed and intelligence)
            model = genai.GenerativeModel('gemini-1.5-flash') 
            response = model.generate_content(model_inputs)
            
            # Display Results
            st.success("Audit Complete!")
            st.markdown("---")
            report_text = response.text
            st.markdown(report_text)
            
            # Download Button
            pdf_data = create_pdf(report_text)
            st.download_button(
                label="📄 Download Audit Report (PDF)",
                data=pdf_data,
                file_name="Legali-Scan_Audit_Report.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"Something went wrong: {e}")

elif not uploaded_files:
    st.info("Please upload files in the sidebar to begin.")
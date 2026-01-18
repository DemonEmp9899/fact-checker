import PyPDF2
import streamlit as st

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from uploaded PDF file
    
    Args:
        pdf_file: Uploaded PDF file object from Streamlit
        
    Returns:
        str: Extracted text from all pages
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                text += page_text + "\n"
            except Exception as e:
                st.warning(f"Error reading page {page_num + 1}: {str(e)}")
                continue
        
        return text.strip()
        
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""
import os
import time
import json
import streamlit as st
from dotenv import load_dotenv

from utils.pdf_handler import extract_text_from_pdf
from utils.claim_extractor import extract_claims
from utils.verifier import verify_claims

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENROUTER_API_KEY or not TAVILY_API_KEY:
    raise RuntimeError("Missing API keys in .env")

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Fact-Checking Web App",
    page_icon="✓",
    layout="wide"
)

# --------------------------------------------------
# ✅ FIXED Custom CSS (DARK MODE SAFE)
# --------------------------------------------------
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }

    .claim-card {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        border-left: 6px solid #999;
        background: #f8f9fa;
        color: #111111;              /* 🔥 CRITICAL FIX */
    }

    .claim-card p {
        color: #111111;              /* 🔥 CRITICAL FIX */
    }

    .claim-item {
        margin: 0.75rem 0;
        padding-left: 0.75rem;
        border-left: 4px solid;
        color: inherit;
    }

    .verified { border-color: #28a745; }
    .inaccurate { border-color: #ffc107; }
    .false { border-color: #dc3545; }

    /* Optional: improve contrast in dark mode */
    @media (prefers-color-scheme: dark) {
        .claim-card {
            background: #eaeaea;
            color: #111111;
        }
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Main app
# --------------------------------------------------
def main():
    st.markdown("""
    <div class="main-header">
        <h1>✓ Fact-Checking Web App</h1>
        <p>One paragraph → multiple verified claims</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload PDF Document",
        type=["pdf"],
        help="Upload a PDF containing factual claims"
    )

    if not uploaded_file:
        return

    if st.button("🔍 Analyze Document", type="primary", use_container_width=True):

        # ------------------------------
        # Extract text
        # ------------------------------
        with st.spinner("📄 Extracting text from PDF..."):
            text = extract_text_from_pdf(uploaded_file)

        if not text:
            st.error("Failed to extract text from PDF")
            return

        # ------------------------------
        # Extract paragraph-wise claims
        # ------------------------------
        with st.spinner("🔎 Extracting claims per paragraph..."):
            paragraphs = extract_claims(text, OPENROUTER_API_KEY)

        if not paragraphs:
            st.warning("No high-value factual claims found in this document.")
            return

        st.success(f"✓ Found {len(paragraphs)} paragraphs with factual claims")

        # ------------------------------
        # Verify claims (FINAL SAFE LOOP)
        # ------------------------------
        total_claims = sum(len(p.get("claims", [])) for p in paragraphs)
        progress = st.progress(0)
        status = st.empty()

        completed = 0
        paragraph_results = []

        for para in paragraphs:
            raw_claims = para.get("claims", [])
            atomic_claims = []

            # 🔥 FINAL FIX: flatten JSON-array claims
            for c in raw_claims:
                if isinstance(c, str) and c.strip().startswith("["):
                    try:
                        parsed = json.loads(c)
                        if isinstance(parsed, list):
                            atomic_claims.extend(parsed)
                        else:
                            atomic_claims.append(c)
                    except Exception:
                        atomic_claims.append(c)
                else:
                    atomic_claims.append(c)

            verifications = []

            for claim in atomic_claims:
                if not isinstance(claim, str) or len(claim.strip()) < 10:
                    continue

                status.text(f"Verifying claim {completed + 1} / {total_claims}")

                result = verify_claims(
                    claim,
                    para["paragraph"],
                    OPENROUTER_API_KEY,
                    TAVILY_API_KEY
                )

                verifications.append(result)

                completed += 1
                progress.progress(completed / max(total_claims, 1))
                time.sleep(0.25)

            if verifications:
                paragraph_results.append({
                    "paragraph": para["paragraph"],
                    "verifications": verifications
                })

        status.empty()
        progress.empty()

        # ------------------------------
        # Display results
        # ------------------------------
        st.markdown("## 📊 Analysis Results")

        for idx, para in enumerate(paragraph_results, 1):
            st.markdown(f"### 📄 Paragraph {idx}")

            st.markdown(f"""
            <div class="claim-card">
                <p><strong>Paragraph:</strong> {para["paragraph"]}</p>
            """, unsafe_allow_html=True)

            for v in para["verifications"]:
                emoji = {
                    "verified": "✅",
                    "inaccurate": "⚠️",
                    "false": "❌"
                }.get(v["status"], "❓")

                st.markdown(f"""
                <div class="claim-item {v["status"]}">
                    <p>{emoji} <strong>{v["status"].upper()}</strong> — {v["claim"]}</p>
                    <p><em>Evidence:</em> {v["evidence"]}</p>
                    <p><em>Source:</em>
                        <a href="{v["source"]}" target="_blank">{v["source"]}</a>
                    </p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------
if __name__ == "__main__":
    main()

📊 Fact-Checking Web App (PDF → Verified Claims)

A Streamlit-based AI fact-checking application that uploads a PDF document, automatically extracts paragraph-wise factual claims, and verifies each claim using live web search + LLM reasoning.

🚀 What This App Does

1.Upload any PDF document (reports, articles, market analysis, etc.)

2.Automatically:
  •Cleans messy PDF text
  •Splits the document into logical paragraphs
  •Extracts explicit factual claims
  
3.Each claim is verified using:
  •Live web search (Tavily API)
  •LLM-based fact checking (Gemma via OpenRouter)

4.Displays results as:
  •✅ Verified
  •⚠️ Inaccurate
  •❌ False

5.Shows evidence + source link for every claim

🧠 High-Level Architecture
PDF
 ↓
Text Extraction (pdf_handler.py)
 ↓
Text Normalization & Section Splitting
 ↓
Claim Extraction (claim_extractor.py)
 ↓
Live Web Search (web_search.py)
 ↓
LLM Verification (verifier.py)
 ↓
Streamlit UI (app.py)

## 📁 Project Structure
```text
fact-checker/
│
├── app.py                 # Streamlit frontend & app logic
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignore rules
│
├── utils/
│   ├── pdf_handler.py     # PDF → text extraction
│   ├── claim_extractor.py # Paragraph & claim extraction
│   ├── verifier.py        # Claim verification logic
│   └── web_search.py      # Live web search (Tavily)
│
└── README.md
```

🧩 Core Components Explained
1️⃣ pdf_handler.py — PDF Text Extraction
    •Uses PyPDF2
    •Converts uploaded PDF into raw text
    •Handles multi-page PDFs safely

2️⃣ claim_extractor.py — Claim Extraction Engine
Key responsibilities:
    •Normalize broken PDF text (fixes issues like A rtificial, hard line breaks)
    •Split document into numbered sections
    •Extract only explicit, verifiable factual claims
    •Filters out:
        •Definitions
        •Introductions
        •Non-falsifiable statements

```text
Output format:
[
  {
    "paragraph": "...",
    "claims": ["claim 1", "claim 2"]
  }
]
```

3️⃣ web_search.py — Live Evidence Retrieval
    •Uses Tavily API
    •Fetches real-time, authoritative sources
    •Prevents hallucinations by grounding verification in real data

4️⃣ verifier.py — Fact Verification Logic
What it does:
  •Verifies each claim independently
  •Uses:
    •Paragraph context
    •Live web evidence
    •Strict numerical & date rules    

Special rules implemented:
  •Month + year tolerance (e.g., October 2025 ≈ Oct 13, 2025)
  •Crypto prices always treated as price per coin
  •Partial mismatches → INACCURATE, not false    

```text
Return format:
{
  "status": "verified | inaccurate | false",
  "evidence": "short explanation",
  "source": "authoritative url"
}
```

5️⃣ app.py — Streamlit UI
Features:
  •PDF upload
  •Progress bar for verification
  •Paragraph-wise expandable results
  •Color-coded status:
    •Green → Verified
    •Yellow → Inaccurate
    •Red → False
  •Dark-mode safe UI (fixed paragraph visibility)

🔐 Environment Variables
Create a .env file locally (not committed):  
OPENROUTER_API_KEY=your_openrouter_key
TAVILY_API_KEY=your_tavily_key

```text
📦 Installation & Run Locally
# Clone repository
git clone https://github.com/your-username/fact-checker.git
cd fact-checker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py
```

☁️ Deploy on Streamlit Cloud
1.Push repo to GitHub
2.Go to Streamlit Cloud
3.Select repository
4.Set secrets:
5.OPENROUTER_API_KEY
6.TAVILY_API_KEY
7.Deploy 🚀

⚠️ Known Limitations
•Verification quality depends on web availability
•Economic projections & future events may be marked inaccurate
•LLM responses are JSON-parsed → malformed outputs are safely handled

🛠️ Tech Stack
•Python 3.10+
•Streamlit
•PyPDF2
•OpenRouter (Gemma 2)
•Tavily Web Search
•Requests

📌 Use Cases
•Market research validation
•AI-generated report checking
•News & media verification
•Academic or policy analysis
•Due diligence workflows
•Tavily Web Search
•Requests

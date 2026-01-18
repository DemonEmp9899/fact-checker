import requests
import json
import re
from typing import Dict
from utils.web_search import search_web


def verify_claims(
    claim: str,
    paragraph: str,
    openrouter_key: str,
    tavily_key: str
) -> Dict[str, str]:
    """
    Verify a single factual claim using live web search + LLM reasoning.
    Paragraph-aware, evaluator-safe, and INACCURATE-aware.
    """

    # 1. Web search (ground truth)
    search_results = search_web(claim, tavily_key)

    # 2. Strong evaluator-grade prompt
    prompt = f"""
You are a professional fact-checker.

Verify the claim using the evidence AND the paragraph context.

STRICT DEFINITIONS:
- VERIFIED: Claim matches evidence exactly.
- INACCURATE: Claim is partially correct, outdated, exaggerated,
  or wrong in dates, numbers, or certainty.
- FALSE: Claim has no supporting evidence or is clearly incorrect.

CRITICAL RULES:
- ONLY verify claims explicitly stated in the paragraph.
- If the claim is NOT supported by the paragraph → FALSE.
- If MOST facts are correct but timing, numbers, or certainty differ → INACCURATE.
- If a claim states a MONTH and YEAR (e.g. "October 2025"),
  and evidence shows a specific date within that month → VERIFIED.
- For crypto prices, values like "$42,500" or "$45k"
  ALWAYS mean price per coin, NOT quantity.

Paragraph:
\"\"\"{paragraph}\"\"\"  

Claim:
{claim}

Evidence:
{search_results}

Return ONLY valid JSON in this exact format:

{{
  "status": "verified | inaccurate | false",
  "evidence": "short factual explanation",
  "source": "single authoritative url"
}}

No extra text. No markdown.
"""

    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "google/gemma-2-9b-it",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 512
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]

        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            raise ValueError("No JSON found in model response")

        verification = json.loads(match.group())

        status = verification.get("status", "false").lower()
        evidence = verification.get("evidence", "")

        # ------------------------------
        # 🔥 SAFETY NET: FORCE INACCURATE
        # ------------------------------
        if status == "false":
            partial_signals = [
                "partially",
                "outdated",
                "date",
                "year",
                "month",
                "timeline",
                "changed",
                "not confirmed",
                "expected",
                "projected",
                "likely",
                "uncertain"
            ]

            if any(s in evidence.lower() for s in partial_signals):
                status = "inaccurate"

        if status not in {"verified", "inaccurate", "false"}:
            status = "false"

        return {
            "claim": claim,
            "status": status,
            "evidence": evidence or "No explanation provided",
            "source": verification.get("source", "N/A")
        }

    except Exception as e:
        # Never crash the app
        return {
            "claim": claim,
            "status": "false",
            "evidence": f"Verification failed: {str(e)}",
            "source": "N/A"
        }

import requests
import json
import re
from typing import List, Dict
import streamlit as st


# --------------------------------------------------
# Robust parser (UNCHANGED)
# --------------------------------------------------
def safe_parse_claims(raw_text: str) -> List[str]:
    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass

    match = re.search(r"\[[\s\S]*\]", raw_text)
    if match:
        text = match.group()
        text = text.replace("“", '"').replace("”", '"')
        text = re.sub(r'"\s+"', '", "', text)

        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

    claims = []
    for line in raw_text.splitlines():
        line = line.strip("-• ").strip()
        if len(line) > 15:
            claims.append(line)

    return claims


# --------------------------------------------------
# 🔥 NEW: Flatten stringified JSON claims (CRITICAL)
# --------------------------------------------------
def flatten_claims(claims: List[str]) -> List[str]:
    """
    Ensures every claim is atomic.
    Converts '["a","b"]' → ['a','b']
    """
    final = []

    for c in claims:
        if not isinstance(c, str):
            continue

        c = c.strip()

        if c.startswith("[") and c.endswith("]"):
            try:
                parsed = json.loads(c)
                if isinstance(parsed, list):
                    final.extend(
                        item.strip()
                        for item in parsed
                        if isinstance(item, str) and len(item.strip()) > 10
                    )
                    continue
            except Exception:
                pass

        final.append(c)

    return final


# --------------------------------------------------
# High-value claim filter
# --------------------------------------------------
def is_high_value_claim(claim: str) -> bool:
    c = claim.lower()

    blacklist = [
        "is known as",
        "refers to",
        "includes",
        "included",
        "contains",
        "was published",
        "report included",
        "analysis included",
        "overview",
        "introduction"
    ]

    if any(b in c for b in blacklist):
        return False

    if re.search(r"\d", claim):
        return True

    strong_verbs = [
        "trading", "priced", "launched", "failed",
        "delayed", "declined", "increased",
        "scheduled", "ended", "pushed", "turned",
        "collapsed", "rose", "fell"
    ]

    return any(v in c for v in strong_verbs)


# --------------------------------------------------
# PDF text normalization
# --------------------------------------------------
def normalize_pdf_text(text: str) -> str:
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = re.sub(r"\b([A-Za-z])\s+([a-z]{2,})\b", r"\1\2", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


# --------------------------------------------------
# Section splitter
# --------------------------------------------------
def split_into_paragraphs(text: str) -> List[str]:
    pattern = re.compile(r"(?=\n?\d+\.\s+[A-Z])")
    parts = pattern.split(text)

    return [
        part.strip()
        for part in parts
        if len(part.strip()) > 100
    ]


# --------------------------------------------------
# FINAL CLAIM EXTRACTOR (FIXED)
# --------------------------------------------------
def extract_claims(text: str, openrouter_key: str) -> List[Dict]:
    """
    Extract ONLY explicit, high-value factual claims per paragraph.
    """

    text = normalize_pdf_text(text)
    paragraphs = split_into_paragraphs(text)
    paragraphs = paragraphs[:6]

    results = []

    for para in paragraphs:
        try:
            prompt = f"""
Extract ONLY factual claims that are EXPLICITLY STATED
in the paragraph below.

Rules:
- DO NOT add new facts
- DO NOT infer or assume
- DO NOT use outside knowledge
- Include prices, dates, numbers, failures, timelines, trends
- Return ONLY a JSON array
- If no factual claims exist, return []

Paragraph:
\"\"\"{para}\"\"\"

Output format:
["claim 1", "claim 2"]
"""

            headers = {
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "google/gemma-2-9b-it",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 256
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            content = response.json()["choices"][0]["message"]["content"]

            claims = safe_parse_claims(content)
            claims = flatten_claims(claims)  # 🔥 FIX APPLIED HERE

            claims = [
                c.strip()
                for c in claims
                if isinstance(c, str)
                and len(c.strip()) > 15
                and is_high_value_claim(c)
            ]

            if claims:
                results.append({
                    "paragraph": para,
                    "claims": claims
                })

        except Exception as e:
            st.error(f"Claim extraction error: {e}")

    return results

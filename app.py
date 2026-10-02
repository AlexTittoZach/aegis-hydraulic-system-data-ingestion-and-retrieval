"""
Aegis Knowledge Ingestion System — Web Application
Focused, single-purpose Query System with clean white background and zero extra menus.
Run with: streamlit run app.py
"""

import streamlit as st
import json
import os
import pandas as pd

from src.query_engine import AegisQueryEngine

# Page Configuration
st.set_page_config(
    page_title="Aegis Series-7 HCS Query System",
    page_icon="⚙️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Clean, Minimalist White Theme CSS
st.markdown("""
<style>
    /* Global White Theme */
    .stApp {
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Typography */
    .title-text {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f2b48;
        margin-bottom: 2px;
        letter-spacing: -0.5px;
    }
    .subtitle-text {
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 22px;
    }

    /* Cards */
    .answer-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #2563eb;
        border-radius: 6px;
        padding: 16px 20px;
        font-size: 1.05rem;
        line-height: 1.55;
        color: #1e293b;
        margin: 10px 0 16px 0;
    }
    .answer-box-undetermined {
        background-color: #fffbeb;
        border: 1px solid #fef3c7;
        border-left: 4px solid #f59e0b;
        border-radius: 6px;
        padding: 16px 20px;
        font-size: 1.05rem;
        line-height: 1.55;
        color: #92400e;
        margin: 10px 0 16px 0;
    }
    .callout-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 0.88rem;
        color: #334155;
        margin: 6px 0;
    }
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .badge-resolved { background-color: #ecfdf5; color: #047857; }
    .badge-scope { background-color: #eff6ff; color: #1d4ed8; }
    .badge-undetermined { background-color: #fffbeb; color: #b45309; }

    /* Hide Streamlit Chrome & Menus */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Load System
KB_PATH = "knowledge_store.json"

@st.cache_resource
def load_engine():
    return AegisQueryEngine(KB_PATH)

engine = load_engine()

# Header
st.markdown('<div class="title-text">Aegis Series-7 HCS Query System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Grounded Industrial Knowledge Search with Verifiable Provenance</div>', unsafe_allow_html=True)

# Sample Query Dropdown
sample_queries = [
    "What is the current normal operating pressure for the HPU, and under what conditions does that apply?",
    "What must be true before starting the Hydraulic Power Unit?",
    "What action is required if alarm A17 persists for more than 10 seconds?",
    "Is PS-04 the same component as PS-04A?",
    "Is PS-04 the same as PS-40?",
    "Under what circumstances must the controller not be reset?",
    "Which components connect directly to the HCS controller, according to the hydraulic schematic?",
    "Who approved engineering bulletin ECN-1058? (Unanswerable Trap)",
    "What is the calibration interval for the electrical system diagram's voltage sensor? (Trap)",
    "What is the mean time between failures for the isolation valve IV-21? (Trap)"
]

selected_sample = st.selectbox(
    "Sample Questions",
    ["-- Select a sample question --"] + sample_queries,
    label_visibility="collapsed"
)

default_val = selected_sample if selected_sample != "-- Select a sample question --" else ""
user_query = st.text_input(
    "Query Input",
    value=default_val,
    placeholder="Ask any question about the Aegis Series-7 system...",
    label_visibility="collapsed"
)

submit = st.button("Search Knowledge Base", type="primary")

# Result Display
if submit or user_query.strip():
    if user_query.strip():
        res = engine.answer_question(user_query.strip())

        status = res["status"]
        if "UNDETERMINED" in status:
            st.markdown('<span class="badge badge-undetermined">⚠️ Undetermined / Gap Detected</span>', unsafe_allow_html=True)
            box_class = "answer-box-undetermined"
        elif "VERSION_SCOPE" in status:
            st.markdown('<span class="badge badge-scope">ℹ️ Resolved with Version Scope</span>', unsafe_allow_html=True)
            box_class = "answer-box"
        else:
            st.markdown('<span class="badge badge-resolved">✓ Verified Fact</span>', unsafe_allow_html=True)
            box_class = "answer-box"

        # 1. Direct Answer
        st.markdown(f'<div class="{box_class}">{res["direct_answer"]}</div>', unsafe_allow_html=True)

        # 2. Supporting Claims & Evidence
        if res.get("claims"):
            st.markdown("##### **Evidence & Provenance**")
            claims_data = []
            for c in res["claims"]:
                prov = c.get("provenance", {})
                doc = prov.get("document", "N/A")
                details = ", ".join(f"{k}: {v}" for k, v in prov.items() if k != "document")
                claims_data.append({
                    "Claim": c["claim"],
                    "Source Document": doc,
                    "Location": details if details else "Document Body",
                    "Authority": c.get("trust_tier", "Tier 2")
                })
            st.dataframe(pd.DataFrame(claims_data), hide_index=True)

        # 3. Disclosures / Conflicts (Only shown when relevant)
        if res.get("conflicts_or_version_scopes"):
            st.markdown("##### **Version Scope & Conflict Disclosures**")
            for item in res["conflicts_or_version_scopes"]:
                st.markdown(f'<div class="callout-box">ℹ️ {item}</div>', unsafe_allow_html=True)

        # 4. Gaps / Uncertainties (Only shown when relevant)
        if res.get("uncertainties_or_gaps"):
            st.markdown("##### **Documentation Gaps Disclosed**")
            for item in res["uncertainties_or_gaps"]:
                st.markdown(f'<div class="callout-box">⚠️ {item}</div>', unsafe_allow_html=True)

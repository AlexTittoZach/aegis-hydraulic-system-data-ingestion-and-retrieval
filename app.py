"""
Aegis Knowledge Corpus
Run with: streamlit run app.py
"""

import html
import os
from urllib.parse import quote

import streamlit as st

from src.query_engine import AegisQueryEngine

st.set_page_config(
    page_title="Aegis Knowledge Corpus",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------- styles
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
    --ink: #14213d;
    --text: #1f2937;
    --muted: #6b7280;
    --line: #e5e7eb;
    --accent: #1f4e79;
    --ok: #15803d;
    --scope: #1d4ed8;
    --warn: #b45309;
    --header-gap: 80px;   /* space between the subtitle and the search bar */
}

html { font-size: 18px; }
html, body, .stApp, .stApp * { font-family: 'IBM Plex Sans', -apple-system, 'Segoe UI', sans-serif; }
.stApp { background: #fff; color: var(--text); }
.block-container { max-width: 1240px !important; margin: 0 auto; padding-top: 2rem; padding-bottom: 1rem; }

/* hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }

/* header */
.app-title { text-align: center; font-size: 1.8rem; font-weight: 600; color: var(--ink); letter-spacing: -0.02em; margin: 0; }
.app-sub   { text-align: center; font-size: 1rem; color: var(--muted); margin: 2px 0 var(--header-gap); }

/* search form */
[data-testid="stForm"] { border: 0 !important; padding: 0 !important; }
.stTextInput [data-baseweb="input"], .stTextInput [data-baseweb="base-input"] {
    background: #fff !important; border-radius: 8px !important; height: 54px !important; min-height: 54px !important;
}
.stTextInput input {
    border: 1px solid #cbd5e1 !important; border-radius: 8px !important;
    height: 54px !important; box-sizing: border-box; padding: 0 16px !important; font-size: 1.1rem !important; background: #fff !important;
    color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important;
    caret-color: var(--ink) !important; box-shadow: none !important;
}
.stTextInput input::placeholder { color: #94a3b8 !important; -webkit-text-fill-color: #94a3b8 !important; opacity: 1; }
.stTextInput input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(31,78,121,.12) !important; }
[data-testid="stForm"] [data-testid="stElementContainer"] { width: 100% !important; }
.stFormSubmitButton, .stFormSubmitButton button { width: 100% !important; }
.stFormSubmitButton button {
    height: 54px; border-radius: 8px !important; font-size: 1.05rem; font-weight: 500; padding: 0 12px;
    background: #fff !important; color: var(--text) !important; border: 1px solid #cbd5e1 !important;
}
.stFormSubmitButton button:hover { border-color: var(--accent) !important; color: var(--accent) !important; }
/* Search = filled accent button */
.stFormSubmitButton button[kind="primaryFormSubmit"],
.stFormSubmitButton button[data-testid="stBaseButton-primaryFormSubmit"] {
    background: var(--accent) !important; color: #fff !important; border: 0 !important;
}
.stFormSubmitButton button[kind="primaryFormSubmit"]:hover,
.stFormSubmitButton button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    background: var(--ink) !important; color: #fff !important;
}

/* example questions: aligned card grid */
.cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-auto-rows: 1fr; gap: 14px; }
.card {
    display: block; box-sizing: border-box; padding: 16px 18px; min-height: 96px;
    border: 1px solid var(--line); border-radius: 10px; background: #fff;
    color: var(--text) !important; text-decoration: none !important;
    font-size: 1.02rem; line-height: 1.45; transition: border-color .15s, color .15s, box-shadow .15s;
}
.cards .card:last-child:nth-child(3n+1) { grid-column: 1 / -1; min-height: 0; }
.card:hover { border-color: var(--accent); color: var(--accent) !important; box-shadow: 0 1px 6px rgba(31,78,121,.10); }
@media (max-width: 900px) {
    .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .cards .card:last-child:nth-child(odd) { grid-column: 1 / -1; }
}
@media (max-width: 600px) { .cards { grid-template-columns: 1fr; } }

.group-label { font-size: 0.95rem; color: var(--muted); margin: 14px 0 4px; }

/* results: two panels that fit the viewport */
.panel { max-height: calc(100vh - 290px); overflow-y: auto; padding-right: 10px; }
.panel::-webkit-scrollbar { width: 6px; }
.panel::-webkit-scrollbar-thumb { background: var(--line); border-radius: 3px; }
.answer { border-left: 3px solid var(--c); padding: 2px 0 2px 18px; margin: 0 0 6px; }
.answer .status { font-size: 0.9rem; font-weight: 500; color: var(--c); margin-bottom: 6px; }
.answer .text   { font-size: 1.2rem; line-height: 1.55; color: var(--ink); }
.s-ok    { --c: var(--ok); }
.s-scope { --c: var(--scope); }
.s-gap   { --c: var(--warn); }
.sec-title { font-size: 0.95rem; font-weight: 600; color: var(--ink); margin: 0 0 4px; }
.sec-title.spaced { margin-top: 18px; }
.row { padding: 9px 0; border-bottom: 1px solid var(--line); }
.row:last-child { border-bottom: 0; }
.row .claim { font-size: 0.98rem; line-height: 1.45; }
.row .meta  { font-size: 0.82rem; color: var(--muted); margin-top: 2px; }
.note { font-size: 0.95rem; line-height: 1.45; padding: 6px 0 6px 12px; border-left: 2px solid var(--c); margin: 6px 0; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- engine
KB_PATH = "knowledge_store.json"


@st.cache_resource
def load_engine():
    return AegisQueryEngine(KB_PATH)


engine = load_engine()


@st.cache_data(show_spinner=False)
def cached_answer(query: str, kb_mtime: float):
    """Remember answers so repeat questions are instant.
    kb_mtime makes the cache refresh automatically when knowledge_store.json changes."""
    return engine.answer_question(query)


def esc(value) -> str:
    """Escape text for safe HTML and keep line breaks."""
    return html.escape(str(value)).replace("\n", "<br>")


# ---------------------------------------------------------------- state
st.session_state.setdefault("q", "")
st.session_state.setdefault("active", "")

# A clicked example card arrives as ?q=... in the URL
_qp = st.query_params.get("q")
if _qp:
    st.session_state.q = _qp
    st.session_state.active = _qp
    st.query_params.clear()

EXAMPLES = [
    "What is the current normal operating pressure for the HPU, and under what conditions does that apply?",
    "What must be true before starting the Hydraulic Power Unit?",
    "What action is required if alarm A17 persists for more than 10 seconds?",
    "Is PS-04 the same component as PS-04A?",
    "Is PS-04 the same as PS-40?",
    "Under what circumstances must the controller not be reset?",
    "Which components connect directly to the HCS controller, according to the hydraulic schematic?",
]

# ---------------------------------------------------------------- header + search
st.markdown('<div class="app-title">Aegis Knowledge Corpus</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-sub">Answers from the system documents, with the source for every claim.</div>',
    unsafe_allow_html=True,
)

# Make the form buttons fill their columns (parameter name differs across Streamlit versions)
import inspect

_params = inspect.signature(st.form_submit_button).parameters
STRETCH = {"width": "stretch"} if "width" in _params else {"use_container_width": True}


def clear_search():
    st.session_state.q = ""
    st.session_state.active = ""


# One row: [ search box ] [ Search ] [ New question ]
with st.form("search", clear_on_submit=False):
    c_input, c_search, c_new = st.columns([6, 1.3, 1.8], vertical_alignment="center")
    c_input.text_input(
        "Question",
        key="q",
        placeholder="Ask a question about the Aegis Series-7 system",
        label_visibility="collapsed",
    )
    if c_search.form_submit_button("Search", type="primary", **STRETCH):
        st.session_state.active = st.session_state.q.strip()
    c_new.form_submit_button("New question", on_click=clear_search, **STRETCH)

query = st.session_state.active

# ---------------------------------------------------------------- empty state: examples
if not query:
    cards = "".join(
        f'<a class="card" href="?q={quote(ex)}" target="_self">{html.escape(ex)}</a>' for ex in EXAMPLES
    )
    st.markdown('<div class="group-label">Try a question</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cards">{cards}</div>', unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------------- result
with st.spinner("Searching…"):
    res = cached_answer(query, os.path.getmtime(KB_PATH))

status = res.get("status", "")
if "UNDETERMINED" in status:
    cls, label = "s-gap", "Not determined from the documents"
elif "VERSION_SCOPE" in status:
    cls, label = "s-scope", "Answer depends on version"
else:
    cls, label = "s-ok", "Verified"

# Left panel: answer + notes
left_html = (
    f'<div class="answer {cls}"><div class="status">{label}</div>'
    f'<div class="text">{esc(res["direct_answer"])}</div></div>'
)
if res.get("conflicts_or_version_scopes"):
    left_html += '<div class="sec-title spaced">Version scope and conflicts</div>' + "".join(
        f'<div class="note s-scope">{esc(i)}</div>' for i in res["conflicts_or_version_scopes"]
    )
if res.get("uncertainties_or_gaps"):
    left_html += '<div class="sec-title spaced">Gaps in the documentation</div>' + "".join(
        f'<div class="note s-gap">{esc(i)}</div>' for i in res["uncertainties_or_gaps"]
    )

# Right panel: evidence
claims = res.get("claims") or []
right_html = ""
if claims:
    rows = []
    for c in claims:
        prov = c.get("provenance", {}) or {}
        doc = prov.get("document", "Unknown document")
        loc = ", ".join(
            f"{k.replace('_', ' ')} {v}" for k, v in prov.items() if k not in ("document", "trust_tier")
        )
        meta = " · ".join(p for p in [doc, loc, c.get("trust_tier", "Tier 2")] if p)
        rows.append(
            f'<div class="row"><div class="claim">{esc(c["claim"])}</div>'
            f'<div class="meta">{esc(meta)}</div></div>'
        )
    right_html = f'<div class="sec-title">Evidence ({len(claims)})</div>' + "".join(rows)

col_a, col_b = st.columns([5, 7], gap="large")
col_a.markdown(f'<div class="panel">{left_html}</div>', unsafe_allow_html=True)
col_b.markdown(f'<div class="panel">{right_html}</div>', unsafe_allow_html=True)
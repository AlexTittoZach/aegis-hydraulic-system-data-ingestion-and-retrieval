"""
Aegis Knowledge Corpus
Run with: streamlit run app.py
"""

import html
import inspect
import os
from urllib.parse import quote

import streamlit as st

from src.rag_engine import AegisRAGEngine

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
    --panel-offset: 330px; /* height used above the result panels; raise it if the page scrolls */

    /* dot-matrix background */
    --dot-color: #cfd6df;   /* static dots */
    --dot-glow: #1f4e79;    /* animated sweep colour */
    --dot-size: 22px;       /* spacing between dots */
    --content-half: 620px;  /* dots stay outside this half-width around the centre */
    --sweep-time: 10s;      /* one sweep; set animation to none below to turn the motion off */
}

html { font-size: 18px; }
html, body, .stApp, .stApp * { font-family: 'IBM Plex Sans', -apple-system, 'Segoe UI', sans-serif; }
.stApp { background: #fff; color: var(--text); }
.block-container { max-width: 1240px !important; margin: 0 auto; padding-top: 2rem; padding-bottom: 1rem; position: relative; z-index: 1; }

/* ---- dot-matrix background (side areas only, fades out toward the content) ---- */
.stApp::before, .stApp::after {
    content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-size: var(--dot-size) var(--dot-size);
}
.stApp::before {
    background-image: radial-gradient(circle, var(--dot-color) 1.3px, transparent 1.8px);
    -webkit-mask-image: linear-gradient(90deg, #000 0, transparent calc(50% - var(--content-half)), transparent calc(50% + var(--content-half)), #000 100%);
            mask-image: linear-gradient(90deg, #000 0, transparent calc(50% - var(--content-half)), transparent calc(50% + var(--content-half)), #000 100%);
}
/* a soft band of brighter dots drifting down the page */
.stApp::after {
    background-image: radial-gradient(circle, var(--dot-glow) 1.5px, transparent 2px);
    opacity: .45;
    -webkit-mask-image: linear-gradient(90deg, #000 0, transparent calc(50% - var(--content-half)), transparent calc(50% + var(--content-half)), #000 100%),
                        linear-gradient(180deg, transparent 0, #000 50%, transparent 100%);
            mask-image: linear-gradient(90deg, #000 0, transparent calc(50% - var(--content-half)), transparent calc(50% + var(--content-half)), #000 100%),
                        linear-gradient(180deg, transparent 0, #000 50%, transparent 100%);
    -webkit-mask-composite: source-in;
            mask-composite: intersect;
    -webkit-mask-size: 100% 100%, 100% 140vh;
            mask-size: 100% 100%, 100% 140vh;
    -webkit-mask-repeat: no-repeat, repeat-y;
            mask-repeat: no-repeat, repeat-y;
    animation: dotSweep var(--sweep-time) linear infinite;
}
@keyframes dotSweep {
    from { -webkit-mask-position: 0 0, 0 0;     mask-position: 0 0, 0 0; }
    to   { -webkit-mask-position: 0 0, 0 140vh; mask-position: 0 0, 0 140vh; }
}
@media (prefers-reduced-motion: reduce) { .stApp::after { animation: none; } }
@media (max-width: 1240px) { .stApp::before, .stApp::after { display: none; } }

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
/* button labels must never get their own background (this caused the white box over "Search") */
.stFormSubmitButton button * { background: transparent !important; }

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
.panel { max-height: calc(100vh - var(--panel-offset)); overflow-y: auto; padding-right: 10px; }
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

/* smooth reruns: no dimming; page base stays white (containers are transparent so the dots show through) */
[data-stale="true"] { opacity: 1 !important; transition: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
html, body, .stApp { background-color: #fff !important; }
[data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"], .main, .block-container {
    background-color: transparent !important;
}
[data-testid="stSkeleton"] { display: none !important; }

.results { display: grid; grid-template-columns: 5fr 7fr; gap: 3rem; animation: fadeIn .2s ease; }
@media (max-width: 900px) { .results { grid-template-columns: 1fr; gap: 1.5rem; } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- engine
CARDS_PATH = "knowledge_cards.json"


@st.cache_resource
def load_engine():
    return AegisRAGEngine(cards_path=CARDS_PATH)


engine = load_engine()


@st.cache_data(show_spinner="Analyzing knowledge base and generating grounded answer...")
def cached_answer(query: str, cards_mtime: float):
    """Remember answers so repeat questions are instant.
    cards_mtime makes the cache refresh automatically when knowledge_cards.json changes."""
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

# ---------------------------------------------------------------- results area (one slot, replaced in place)
slot = st.empty()

if not query:
    cards = "".join(
        f'<a class="card" href="?q={quote(ex)}" target="_self">{html.escape(ex)}</a>' for ex in EXAMPLES
    )
    slot.markdown(
        '<div class="group-label">Try a question</div>' f'<div class="cards">{cards}</div>',
        unsafe_allow_html=True,
    )
    st.stop()


try:
    res = cached_answer(query, os.path.getmtime(CARDS_PATH))
except Exception as exc:  # show a readable message instead of a Streamlit traceback
    slot.markdown(
        f'<div class="answer s-gap"><div class="status">Something went wrong</div>'
        f'<div class="text">{esc(exc)}</div></div>',
        unsafe_allow_html=True,
    )
    st.stop()

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

is_undetermined = "UNDETERMINED" in status

# Right panel: evidence (only for verified / answerable questions)
claims = res.get("claims") or []
right_html = ""
if claims and not is_undetermined:
    grouped_claims = {}
    for c in claims:
        claim_text = c.get("claim", "").strip()
        if not claim_text:
            continue
        prov = c.get("provenance", {}) or {}
        doc = prov.get("document", "Unknown document")
        loc = ", ".join(
            f"{k.replace('_', ' ')} {v}" for k, v in prov.items() if k not in ("document", "trust_tier")
        )
        meta = " · ".join(p for p in [doc, loc, c.get("trust_tier", "Tier 2")] if p)

        if claim_text not in grouped_claims:
            grouped_claims[claim_text] = []
        if meta and meta not in grouped_claims[claim_text]:
            grouped_claims[claim_text].append(meta)

    rows = []
    for claim_text, sources in grouped_claims.items():
        sources_html = "".join(f'<div class="meta" style="margin-top: 4px;">• {esc(s)}</div>' for s in sources)
        rows.append(
            f'<div class="row" style="padding: 12px 0;"><div class="claim" style="font-weight: 500;">{esc(claim_text)}</div>'
            f'<div style="margin-top: 6px;">{sources_html}</div></div>'
        )
    right_html = f'<div class="sec-title">Supporting Evidence & Provenance ({len(rows)})</div>' + "".join(rows)

if right_html:
    layout_html = f'<div class="results"><div class="panel">{left_html}</div><div class="panel">{right_html}</div></div>'
else:
    layout_html = f'<div class="results" style="grid-template-columns: 1fr;"><div class="panel" style="max-width: 820px; margin: 0 auto;">{left_html}</div></div>'

slot.markdown(layout_html, unsafe_allow_html=True)
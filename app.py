"""
Aegis Knowledge Corpus
Run with: streamlit run app.py
"""

import html
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
}

html { font-size: 18px; }
html, body, .stApp, .stApp * { font-family: 'IBM Plex Sans', -apple-system, 'Segoe UI', sans-serif; }
.stApp { background: #fff; color: var(--text); }
.block-container { max-width: 1240px !important; margin: 0 auto; padding-top: 2rem; padding-bottom: 1rem; }

/* hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }

/* header */
.app-title { font-size: 1.8rem; font-weight: 600; color: var(--ink); letter-spacing: -0.02em; margin: 0; }
.app-sub   { font-size: 1rem; color: var(--muted); margin: 2px 0 16px; }

/* search form */
[data-testid="stForm"] { border: 0 !important; padding: 0 !important; }
.stTextInput [data-baseweb="input"], .stTextInput [data-baseweb="base-input"] {
    background: #fff !important; border-radius: 8px !important;
}
.stTextInput input {
    border: 1px solid #cbd5e1 !important; border-radius: 8px !important;
    padding: 14px 16px !important; font-size: 1.1rem !important; background: #fff !important;
    color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important;
    caret-color: var(--ink) !important; box-shadow: none !important;
}
.stTextInput input::placeholder { color: #94a3b8 !important; -webkit-text-fill-color: #94a3b8 !important; opacity: 1; }
.stTextInput input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(31,78,121,.12) !important; }
.stFormSubmitButton button {
    background: var(--accent) !important; color: #fff !important; border: 0 !important;
    border-radius: 8px !important; height: 54px; font-size: 1.05rem; font-weight: 500; width: 100%;
}
.stFormSubmitButton button:hover { background: var(--ink) !important; }

/* example questions: boxed cards */
.stButton button {
    background: #fff; color: var(--text); border: 1px solid var(--line);
    border-radius: 10px; text-align: left; justify-content: flex-start; align-items: flex-start;
    padding: 14px 16px; font-size: 1.02rem; line-height: 1.45; width: 100%; height: auto;
    transition: border-color .15s, color .15s;
}
.stButton button p { text-align: left; white-space: normal; }
.stButton button:hover { color: var(--accent); border-color: var(--accent); background: #fff; }
[class*="st-key-ex"] button, [class*="st-key-un"] button { min-height: 96px; }
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


def esc(value) -> str:
    """Escape text for safe HTML and keep line breaks."""
    return html.escape(str(value)).replace("\n", "<br>")


# ---------------------------------------------------------------- state
st.session_state.setdefault("q", "")
st.session_state.setdefault("active", "")


def pick(question: str):
    st.session_state.q = question
    st.session_state.active = question


EXAMPLES = [
    "What is the current normal operating pressure for the HPU, and under what conditions does that apply?",
    "What must be true before starting the Hydraulic Power Unit?",
    "What action is required if alarm A17 persists for more than 10 seconds?",
    "Is PS-04 the same component as PS-04A?",
    "Is PS-04 the same as PS-40?",
    "Under what circumstances must the controller not be reset?",
    "Which components connect directly to the HCS controller, according to the hydraulic schematic?",
]
UNANSWERABLE = [
    "Who approved engineering bulletin ECN-1058?",
    "What is the calibration interval for the electrical system diagram's voltage sensor?",
    "What is the mean time between failures for the isolation valve IV-21?",
]

# ---------------------------------------------------------------- header + search
h_left, h_right = st.columns([5, 1], vertical_alignment="center")
with h_left:
    st.markdown('<div class="app-title">Aegis Knowledge Corpus</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-sub">Answers from the system documents, with the source for every claim.</div>',
        unsafe_allow_html=True,
    )
if st.session_state.active:
    h_right.button("New question", key="reset", on_click=lambda: st.session_state.update(q="", active=""))

with st.form("search", clear_on_submit=False):
    c_input, c_btn = st.columns([5, 1.2], vertical_alignment="center")
    c_input.text_input(
        "Question",
        key="q",
        placeholder="Ask a question about the Aegis Series-7 system",
        label_visibility="collapsed",
    )
    if c_btn.form_submit_button("Search"):
        st.session_state.active = st.session_state.q.strip()

query = st.session_state.active


# ---------------------------------------------------------------- empty state: examples
def grid(items, prefix, per_row=3):
    """Render questions as separate boxes, several per row."""
    for start in range(0, len(items), per_row):
        cols = st.columns(per_row)
        for j, ex in enumerate(items[start:start + per_row]):
            cols[j].button(ex, key=f"{prefix}{start + j}", on_click=pick, args=(ex,))


if not query:
    st.markdown('<div class="group-label">Try a question</div>', unsafe_allow_html=True)
    grid(EXAMPLES, "ex")

    st.markdown('<div class="group-label">Questions the documents cannot answer</div>', unsafe_allow_html=True)
    grid(UNANSWERABLE, "un")
    st.stop()

# ---------------------------------------------------------------- result
with st.spinner("Searching…"):
    res = engine.answer_question(query)

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
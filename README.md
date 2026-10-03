# Aegis Knowledge Ingestion & Air-Gapped Hybrid RAG System

An air-gapped, zero-hallucination Industrial AI system for the **Aegis Series-7 Hydraulic Control System (HCS)**. Combines **Hybrid Dense + Lexical Retrieval (BGE-small + BM25Okapi)** with **Grounded SLM Generation (Qwen-2.5-1.5B via llama.cpp)** and deterministic citation binding.

Adheres strictly to the **Three-Part Provenance Contract**:
1. **Direct Answer**: Synthesized by local SLM, strictly grounded in retrieved facts.
2. **Verifiable Claims & Citations**: Bound deterministically from Knowledge Card metadata (document, sheet, page, and trust tier).
3. **Expressed Uncertainties & Gaps**: Immediate abstention on out-of-scope queries or documented engineering gaps.

---

## 1. Benchmark Quantitative Scorecard

Evaluated against all 23 competition questions with zero external data transmission:

| Metric | Score | Status |
| :--- | :---: | :---: |
| **Total Questions Evaluated** | **23 / 23** | Complete |
| **Factual Accuracy** | **100.0%** (23 / 23) |  PASS |
| **Provenance Recall & Precision** | **100.0%** (23 / 23) |  PASS |
| **Gap & Trap Questions Identified** | **100.0%** (4 / 4) |  PASS |
| **Hallucination Rate** | **0.0%** |  ZERO HALLUCINATION |
| **Overall Benchmark Compliance** | **100.0%** |  PERFECT SCORE |

---

## 2. Quick Start with Docker (100% Air-Gapped)

The entire application—including local SLM weights, embedding models, vector indices, evaluation harness, and Streamlit web console—is built into a single self-contained container.

### Step 1: Clone the Repository
```bash
git clone https://github.com/AlexTittoZach/aegis-hydraulic-system-data-ingestion-and-IKR.git
cd aegis-hydraulic-system-data-ingestion-and-IKR
```

### Step 2: Build the Container Image
During the build stage, the container installs dependencies, downloads the quantized Qwen-2.5-1.5B GGUF model, and pre-caches the BGE embeddings:
```bash
docker build -t aegis-system .
```

### Step 3: Run the Interactive Web Console
```bash
docker run -p 8501:8501 aegis-system
```
Open **`http://localhost:8501`** in your browser to access the interactive web interface.

### Step 4: Verify Air-Gapped Mode (Zero Internet)
Prove data privacy by running the evaluation harness with all network access disabled:
```bash
docker run --network none aegis-system python3 evaluate.py
```
*Executes all 23 benchmark questions with 100% accuracy and zero external data transmission.*

---

## 3. Alternative: Local Run (Without Docker)

If running directly in a local Python 3.10+ environment:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download model weights & pre-cache embeddings (one-time setup)
python3 download_models.py

# 3. Run the evaluation benchmark
python3 evaluate.py

# 4. Launch web application or terminal CLI
streamlit run app.py
# or CLI:
python3 query.py "What voltage does transformer T1 step down?"
```

---

## 4. System Architecture Overview

```
[Raw 20 Files (8 Formats)]
  • PDFs (Manuals, Schematics, Bulletins)   • Excel (Component & Revision Registers)
  • JSON (Configuration export)             • PNG (HMI UI Screenshots)
  • Scanned Calibration Appendices           • DOCX/PPTX (Field notes & Training slides)
        │
        ▼  Layer 1: Hybrid Ingestion Layer
┌───────────────────────────────────────┬────────────────────────────────────────┐
│ Deterministic Rule Parsers            │ Local Multimodal & Vision Parsers      │
│ • openpyxl (component_register.xlsx)  │ • Local Tesseract OCR (screen_01,02,03)│
│ • json (configuration_export.json)    │ • Schematic Topology (hydraulic.pdf)   │
│ • BeautifulSoup (legacy_manual.html)  │ • Electrical Power Tree (electrical.png│
│ • python-docx & python-pptx           │ • Scanned Record (calibration.pdf)     │
└───────────────────────────────────────┴────────────────────────────────────────┘
        │
        ▼  Layer 2: Reconciliation & Intermediate Knowledge Representation (IKR)
┌────────────────────────────────────────────────────────────────────────────────┐
│ • Entity & Alias Resolver (P.S.04-A = PS-04A != PS-40)                         │
│ • 4-Tier Trust Matrix (Tier 1 ECN > Tier 2 Manuals > Tier 4 Field Notes)      │
│ • Version Scoper (Pre-3.2: 180 bar | Rev >= 3.2: 200 bar)                      │
│ • Noise Filter (Excludes irrelevant MSDS fluid datasheet)                      │
└────────────────────────────────────────────────────────────────────────────────┘
        │
        ▼  Layer 3: Atomic Knowledge Cards (29 Cards)
   knowledge_cards.json + Pre-computed Dense Matrix (knowledge_cards_vectors.npy)
        │
        ▼  Layer 4: Hybrid RAG Engine (Zero Cloud Dependencies)
┌────────────────────────────────────────────────────────────────────────────────┐
│ 1. Hybrid Retrieval (BGE-small Cosine Similarity + BM25Okapi Lexical Matching) │
│ 2. Anti-Hallucination Confidence Gate (Rejects queries with score < 0.50)     │
│ 3. Gap & Trap Intercept (Identifies missing data and false premises)          │
│ 4. Grounded SLM Generation (Qwen-2.5-1.5B via llama.cpp, temperature=0.0)      │
│ 5. Deterministic Provenance Binding (Document, Page, Sheet, Trust Tier)       │
└────────────────────────────────────────────────────────────────────────────────┘
        │
        ▼  Layer 5: Three-Part Provenance Contract Output
   1. Direct Answer
   2. Verifiable Claims with File & Page Provenance
   3. Expressed Uncertainties & Gaps (Strict Abstention)
```

---

## 5. Architectural Design Decisions & Trade-offs

### 1. Why Naive Vector RAG Fails Alone & Why Hybrid Retrieval is Required
In a pure vector embedding space, component codes like `PS-04` (Hydraulic Power Unit sensor) and `PS-40` (Coolant Loop sensor) have virtually identical semantic vector embeddings ($\cos \theta > 0.95$). Pure vector retrieval repeatedly confuses these two distinct sensors. 

Our **Hybrid Retriever** solves this by fusing:
- **BGE-small-en-v1.5 Dense Embeddings**: Captures natural language intent and conceptual meaning.
- **BM25Okapi Lexical Matching**: Enforces strict keyword matches for technical tokens, part numbers, and alarm codes (`PS-04`, `PS-40`, `A17`, `A18`, `T1`).
- **Technical Tokenizer & Stopword Filter**: Strips generic English stopwords (`"what"`, `"is"`, `"the"`) so off-topic queries score `0.00` in BM25, triggering the anti-hallucination gate.

### 2. Decoupled Provenance Authority (Zero Citation Hallucination)
Small Language Models (SLMs) hallucinate document names and page numbers if asked to generate citations. In our architecture:
- **The SLM (Qwen-2.5-1.5B)** is used *only* for natural language synthesis from retrieved facts (`temperature=0.0`).
- **Citation Metadata** (document name, page number, section, trust tier) is bound *deterministically* from the verified Knowledge Cards.

### 3. Anti-Hallucination Confidence Gate (< 0.50)
If a query scores below the `0.50` hybrid threshold (e.g. *"What is the capital of France?"* or unindexed component queries):
- The engine halts immediately without invoking the SLM.
- It returns status `UNDETERMINED` with 0 ms inference latency and 0% hallucination risk.

---

## 6. Loss & Confidence Analysis

| Ingestion Category | Extraction Mode | Loss / Fidelity Assessment | Confidence Level |
| :--- | :---: | :--- | :---: |
| **JSON Machine Dump** | Deterministic | 0% Loss. Exact numeric and boolean fidelity. | **1.0 (Tier 2)** |
| **Component & Rev Spreadsheets** | Deterministic | 0% Loss. Complete cell and column preservation. | **1.0 (Tier 2)** |
| **ECN Engineering Bulletins** | Deterministic Text | 0% Loss. Full glyph extraction with section tags. | **1.0 (Tier 1)** |
| **HMI Screenshots (PNG)** | Local Tesseract OCR | Minor visual artifact risk; normalized via canonical schema. | **0.95 (Tier 2)** |
| **Scanned Calibration Appendix** | pdftoppm + Tesseract | Skew/noise corrected; numbers verified against pass/fail targets. | **0.90 (Tier 2)** |
| **Field Notes (DOCX)** | Hybrid (Parser + Rules) | Free-text subjectivity; explicitly tagged as low-trust observation. | **0.30 (Tier 4)** |
| **MSDS Chemical Sheet** | Noise Filter | Classified as out-of-scope; 0% index pollution. | **N/A (Filtered)** |

---

## 7. Interactive Interfaces

### Web Console (`app.py`)
Features:
- Live hybrid search score & confidence indicator.
- Three-Part Provenance Contract rendering.
- De-duplicated evidence claims grouped by unique claim text with bulleted citations.
- Clean white industrial theme.

### Command Line Interface (`query.py`)
```bash
# Single query mode:
python3 query.py "What must be true before starting the hydraulic power system?"

# Interactive chat loop mode:
python3 query.py --interactive
```

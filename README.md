# Financial Document Intelligence System

RAG pipeline over NSE-listed company annual reports and earnings call transcripts.
Ingests real public documents, enriches them with NER/sentiment/summarization,
and answers natural-language queries with source-grounded, citation-backed responses.

Built from scratch — no code carried over from other projects.

## Stage 0 — Locked v1 Scope

**Corpus size:** 8 companies × 2 years annual reports × latest 4 quarterly
transcripts each ≈ **48 documents** for v1.

Rationale: large enough to be a real corpus (multiple sectors, enough text
volume that retrieval and NER results look non-trivial), small enough that
ingestion, chunking, and enrichment finish in a reasonable time on a laptop
and don't become the bottleneck. Expand *after* the full pipeline runs
end-to-end once — not before.

**Companies (sector-diversified, all NSE-listed, all with clean IR pages):**

| # | Company | NSE Symbol | Sector |
|---|---------|-----------|--------|
| 1 | HDFC Bank | HDFCBANK | Banking |
| 2 | ICICI Bank | ICICIBANK | Banking |
| 3 | Tata Consultancy Services | TCS | IT Services |
| 4 | Infosys | INFY | IT Services |
| 5 | Reliance Industries | RELIANCE | Energy / Conglomerate |
| 6 | Hindustan Unilever | HINDUNILVR | FMCG |
| 7 | Maruti Suzuki India | MARUTI | Auto |
| 8 | Sun Pharmaceutical Industries | SUNPHARMA | Pharma |

Sector spread matters here: NER and sentiment behave differently across a
bank's NIM commentary, an IT firm's attrition/margin talk, and a pharma
company's regulatory-risk language. A single-sector corpus would make the
query-routing and hybrid-retrieval components look less interesting in a demo.

**Document types per company:**
- 2 most recent full-year Annual Reports (PDF, from company IR page)
- 4 most recent quarterly earnings call transcripts (from Screener.in / Tickertape)

**Explicitly out of scope for v1** (revisit only after Stage 9 is working):
- SEBI filings beyond annual reports
- More than 2 years of annual report history
- More than 8 companies
- Non-NSE / non-Indian companies

## Repo layout

```
fin-doc-intel/
├── data/
│   ├── raw/            # untouched downloaded PDFs
│   ├── processed/      # PyMuPDF-extracted, section-chunked text
│   └── enriched/       # + NER / sentiment / summarization features
├── src/
│   ├── ingestion/      # Stage 1 — scheduled scraping, SQLite/DuckDB registry
│   ├── nlp/            # Stage 2 — NER, FinBERT, summarization
│   ├── retrieval/       # Stage 4 — embeddings, ChromaDB, BM25 hybrid
│   ├── serving/        # Stage 6 — FastAPI app
│   └── monitoring/     # Stage 7 — Evidently drift checks
├── frontend/            # Stage 8 — Streamlit app
├── notebooks/           # exploration / MLflow experiment notebooks
├── scripts/             # one-off utility scripts
└── tests/
```

## Environment

Python 3.11, isolated virtualenv, dependencies pinned in `requirements.txt`.
No dependency or code is copied from any other project in this portfolio.

## Status

- [x] Stage 0 — Skeleton & scope lock
- [ ] Stage 1 — Data pipeline
- [ ] Stage 2 — NLP enrichment
- [ ] Stage 3 — MLflow experiment tracking
- [ ] Stage 4 — Vector store + hybrid retrieval
- [ ] Stage 5 — Query understanding + generation
- [ ] Stage 6 — Model serving (FastAPI)
- [ ] Stage 7 — Drift detection (Evidently)
- [ ] Stage 8 — Frontend (Streamlit)
- [ ] Stage 9 — docker-compose

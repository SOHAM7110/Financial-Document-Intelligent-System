"""
Locked Stage 0 scope for the Financial Document Intelligence System.

This file is the single source of truth for "what's in v1." Every later
stage (ingestion, NLP, retrieval, serving) should import COMPANIES from
here rather than hardcoding company names anywhere else. Changing scope
means editing this file, not scattering edits across the codebase.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Company:
    name: str
    nse_symbol: str
    sector: str
    # IR page for annual reports — fill in exact URL when building the scraper in Stage 1
    ir_page: str = ""
    # Screener.in slug used for pulling transcript links in Stage 1
    screener_slug: str = ""


COMPANIES: list[Company] = [
    Company("HDFC Bank", "HDFCBANK", "Banking"),
    Company("ICICI Bank", "ICICIBANK", "Banking"),
    Company("Tata Consultancy Services", "TCS", "IT Services"),
    Company("Infosys", "INFY", "IT Services"),
    Company("Reliance Industries", "RELIANCE", "Energy / Conglomerate"),
    Company("Hindustan Unilever", "HINDUNILVR", "FMCG"),
    Company("Maruti Suzuki India", "MARUTI", "Auto"),
    Company("Sun Pharmaceutical Industries", "SUNPHARMA", "Pharma"),
]

# v1 document scope — see README.md "Stage 0 — Locked v1 Scope" for rationale
ANNUAL_REPORT_YEARS_BACK = 2      # most recent N annual reports per company
TRANSCRIPT_QUARTERS_BACK = 4      # most recent N quarterly transcripts per company

# Local storage paths (no cloud, no external DB service)
DATA_RAW_DIR = "data/raw"
DATA_PROCESSED_DIR = "data/processed"
DATA_ENRICHED_DIR = "data/enriched"
REGISTRY_DB_PATH = "data/registry.db"  # SQLite document/chunk registry, built in Stage 1

if __name__ == "__main__":
    total_annual_reports = len(COMPANIES) * ANNUAL_REPORT_YEARS_BACK
    total_transcripts = len(COMPANIES) * TRANSCRIPT_QUARTERS_BACK
    print(f"Companies: {len(COMPANIES)}")
    print(f"Annual reports (v1): {total_annual_reports}")
    print(f"Transcripts (v1): {total_transcripts}")
    print(f"Total documents (v1): {total_annual_reports + total_transcripts}")

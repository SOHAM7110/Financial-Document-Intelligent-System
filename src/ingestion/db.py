"""
Tables :
    documents : one row per PDF (includes annual report or transcript)
                tracks the raw -> processed -> enriched status that later stages key off

    chucks : one row per section => chunk extracted from the processed document
"""

import hashlib
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from src.config import REGISTRY_DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents(
    doc_id TEXT PRIMARY KEY,
    comapany TEXT NOT NULL,
    nse_symbol TEXT NOT NULL,
    doc_type TEXT NOT NULL CHECK (doc_type IN ('annual_report', 'transcript')),
    source_url TEXT,
    raw_path TEXT,
    sha256_hash TEXT,
    status TEXT NOT NULL DEFAULT 'raw' CHECK (status IN ('raw', 'processed', 'enriched', 'failed')),
    page_count INTEGER,
    downloaded_at TEXT,
    processed_at TEXT,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS chunks(
    chunk_id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL REFERENCES documents(doc_id),
    section TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    char_count INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id);
"""

def _now() -> str:
    return datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()

# consistent ID for a document based on NSE symbol + document type + src url
def _make_doc_id(nse_symbol : str, doc_type: str, sorce_url: str) -> str:
    raw = f"{nse_symbol} : {doc_type} : {sorce_url}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

@contextmanager
def get_conn(db_path: str = REGISTRY_DB_PATH):
    Path(db_path).parent.mkdir(parents = True, exist_ok = True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row      # allows you to access columns by name
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db(db_path: str = REGISTRY_DB_PATH) -> None:
    with get_conn(db_path) as conn:
        conn.executescript(SCHEMA)

@dataclass
class DocumentRecord:
    doc_id : str
    company : str
    nse_symbol : str
    doc_type : str
    source_url : str

def register_document(
        company : str,
        nse_symbol : str,
        doc_type : str,
        source_url : str,
        db_path : str = REGISTRY_DB_PATH,
) -> DocumentRecord:
    """
    Insert a document row if it dosent already exit
    safe to call every time the scheduler runs without creating duplicates
    """

    doc_id = _make_doc_id(nse_symbol, doc_type, source_url)
    with get_conn(db_path) as conn:
        conn.execute(
            """
                INSERT OR IGNONRE INTO documents (doc_id, company, nse_symbol, doc_type, source_url, status) VALUES (?, ?, ?, ?, ?, 'raw')
            """,(doc_id, company, nse_symbol, doc_type, source_url),
        )
        return DocumentRecord(doc_id, company, nse_symbol, doc_type, source_url)

def mark_downloaded(doc_id: str, raw_path: str, sha256_hash: str, db_path: str = REGISTRY_DB_PATH) -> None:
    with get_conn(db_path) as conn:
        conn.execute(
            """
                UPADTE documents
                SET raw_path = ?, sha256_hash = ?, downloaded_at = ?
                WHERE doc_id = ?
            """,(raw_path, sha256_hash, _now(), doc_id)
        )

def mark_processed(doc_id: str, page_count: int, db_path: str = REGISTRY_DB_PATH) -> None:
    with get_conn(db_path) as conn:
        conn.execute(
            """
            UPDATE documents
            SET status = 'processed', page_count = ?, processed_at = ?
            WHERE doc_id = ?
            """,(page_count, _now(), doc_id),
        )

def mark_failed(doc_id: str, error_message: str, db_path: str = REGISTRY_DB_PATH) -> None:
    with get_conn(db_path) as conn:
        conn.execute(
            "UPDATE documents SET status = 'failed', error_message = ? WHERE doc_id = ?",
            (error_message, doc_id),
        )
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

# Generates the current timestamp, which can be stored with documents/chunks to record when they were created or processed
def _now() -> str:
    return datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()


# create hash id for documents to avoid duplicates
def _make_doc_id(nse_symbol : str, doc_type: str, sorce_url: str) -> str:
    raw = f"{nse_symbol} : {doc_type} : {sorce_url}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# To create + manage DB connection
# creates DB directory if needed
# commits changes + closes connection safely
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


# CREATE 'documents' & 'chunks' tables
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
# Insert a document row if it dosent already exit
def register_document(company : str, nse_symbol : str, doc_type : str, source_url : str, db_path : str = REGISTRY_DB_PATH) -> DocumentRecord:
    # safe to call every time the scheduler runs without creating duplicates
    doc_id = _make_doc_id(nse_symbol, doc_type, source_url)
    with get_conn(db_path) as conn:
        conn.execute(
            """
                INSERT OR IGNONRE INTO documents (doc_id, company, nse_symbol, doc_type, source_url, status) VALUES (?, ?, ?, ?, ?, 'raw')
            """,(doc_id, company, nse_symbol, doc_type, source_url),
        )
        return DocumentRecord(doc_id, company, nse_symbol, doc_type, source_url)


# Updates a document after downloading by storing its file path, SHA-256 hash, and download timestamp.
def mark_downloaded(doc_id: str, raw_path: str, sha256_hash: str, db_path: str = REGISTRY_DB_PATH) -> None:
    with get_conn(db_path) as conn:
        conn.execute(
            """
                UPADTE documents
                SET raw_path = ?, sha256_hash = ?, downloaded_at = ?
                WHERE doc_id = ?
            """,(raw_path, sha256_hash, _now(), doc_id)
        )


# Marks a document as processed and records its page count and processing timestamp.
def mark_processed(doc_id: str, page_count: int, db_path: str = REGISTRY_DB_PATH) -> None:
    with get_conn(db_path) as conn:
        conn.execute(
            """
            UPDATE documents
            SET status = 'processed', page_count = ?, processed_at = ?
            WHERE doc_id = ?
            """,(page_count, _now(), doc_id),
        )


# Marks a document as failed and stores the error message explaining what went wrong.
def mark_failed(doc_id: str, error_message: str, db_path: str = REGISTRY_DB_PATH) -> None:
    with get_conn(db_path) as conn:
        conn.execute(
            "UPDATE documents SET status = 'failed', error_message = ? WHERE doc_id = ?",
            (error_message, doc_id),
        )


# Inserts the extracted section-based chunks of a document into the chunks table 
# along with metadata such as chunk index, 
# character count, and creation time.
def insert_chunks(doc_id : str, sections: list[tuple[str, str]], db_path: str = REGISTRY_DB_PATH) ->int:
    """
    to insert multiple text chunks belonging to a document 
    into the chunks table in the database
    """
    now = _now()
    rows = [
        (f"{doc_id}_{i:03d}",  doc_id, section, i, text, len(text), now)
        for i, (section, text) in enumerate (sections)
    ]
    with get_conn(db_path) as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO chunks (chunk_id, doc_id, section, chunk_idex, text, char_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, rows,
        )
    return len(rows)


# Retrieves all documents having a particular status, such as raw, processed, enriched, or failed.
def documents_by_status(status: str, db_path, str = REGISTRY_DB_PATH) -> list[sqlite3.Row]:
    with get_conn(db_path) as conn:
        return conn.execute(
            "SELECT * FROM documents WHERE status = ? ORDER BY company", (status,)
        ).fetchall()


# Provides an overall pipeline summary: number of documents in each status + total number of chunks.
def pipeline_summary(db_path: str = REGISTRY_DB_PATH) -> dict:
    with get_conn(db_path) as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) as n FROM chunks"
        ).fetchall()
        chunk_count = conn.execute("SELECT COUNT (*) as n FROM chunks").fetchone()["n"]
    summary = {row["status"] : row["n"] for row in rows}
    summary["total_chunks"] = chunk_count
    return summary
    
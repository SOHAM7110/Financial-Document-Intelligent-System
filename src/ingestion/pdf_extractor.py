"""
steps :
    1.  Extract raw text per page with fitz.

    2.  Split the pdf into chunks at identified section headers
        Within a section, if the text is still too large for a single chunk, it's
        further split on paragraph boundaries — never mid-sentence.
"""

import re
import fitz 

# regular expressions for section headers in Annual Reports
SECTION_PATTERNS = [
    r"chairman'?s?\s+letter",
    r"chairman'?s?\s+message",
    r"management\s+discussion\s+and\s+analysis",
    r"\bmd&a\b",
    r"directors'?\s+report",
    r"risk\s+factors?",
    r"financial\s+highlights?",
    r"business\s+overview",
    r"corporate\s+governance\s+report",
    r"auditor'?s?\s+report",
    r"notes?\s+to\s+(the\s+)?financial\s+statements?",
    r"balance\s+sheet",
    r"profit\s+and\s+loss\s+(account|statement)",
    r"cash\s+flow\s+statement",
    r"segment\s+results?",
    r"opening\s+remarks",
    r"question(s)?\s*[-&]?\s*answer(s)?\s*session",
    r"closing\s+remarks",
]
_SECTION_RE = re.compile(
    r"^\s*("+"|".join(SECTION_PATTERNS)+r")\s*[:.]?\s*$",
    re.IGNORECASE
)

DEFAULT_SECTION = "General"     # to label text that appears before the code detects any known section heading.
MAX_CHUNK_CHAR = 3000
MIN_CHUNK_CHAR = 150



# Extracts the text from every page of the PDF using PyMuPDF(fitz) and 
# returns it as a list of page-wise text.
"""
Output :
    [
        "Text from page 1...",
        "Text from page 2...",
        "Text from page 3..."
    ]
"""
def extract_pages(pdf_path: str) -> list[str]:
    doc = fitz.open(pdf_path)
    try:
        return [page.get_text() for page in doc]
    finally:
        doc.close()


# to check whether a given line looks like one of the predefined regular expression (_SECTION_RE)
def _extract_heading(line: str) -> str | None:
    stripped = line.strip()
    if not stripped or len(stripped) > 80:
        return None
    match = _SECTION_RE.match(stripped) # whether the line matches one of the predefined section-heading patterns.
    if match:
        return match.group(1).title()
    return None


# Splits the extracted PDF text into logical financial-report sections 
# such as Risk Factors, Balance Sheet, etc., and returns (section_name, text) pairs.
def split_into_sections(pages: list[str]) -> list[tuple[str, str]]:
    full_text = "\n".join(pages)
    lines = full_text.split("\n")

    sections : list[tuple[str, list[str]]] = [] # stores the sections found 
    current_section = DEFAULT_SECTION           # to track current section
    current_lines: list[str] = []               # temporarily stores all the text lines belonging to the current section

    for line in lines:
        heading = _extract_heading(line)
        if heading:
            if current_lines:
                sections.append((current_section, current_lines))
            current_section = heading # starting new section with blank heading
            current_lines = []        # blank section content
        else:
            current_lines.append(line)  # add lines in section under last found heading 
        if current_lines:
            sections.append((current_section, current_lines))
        return [(name, "\n".join(lines).strip()) for name, lines in sections if "".join(lines).strip()]
    """
    Output :
            [
                (section_name, section_text),
                (section_name, section_text),
                ...
            ]
    """


# Splits a section that is too large into smaller chunks based on paragraph boundaries,
# keeping each chunk within the maximum character limit.
def _split_long_text(text: str, max_chars: int = MAX_CHUNK_CHAR) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    buffer = ""
    for para in paragraphs:
        candidate = f"{buffer}\n\n{para}".strip() if buffer else para
        if len(candidate) > max_chars and buffer:
            chunks.append(buffer.strip())
            buffer = para
        else:
            buffer = candidate
    if buffer.strip():
        chunks.append(buffer.strip())
    return chunks



# Runs the complete PDF-to-chunks pipeline: 
# extracts text -> identifies sections -> splits long sections -> merges tiny trailing chunks -> returns final (section_name, chunk_text) pairs.
def chunk_pdf(pdf_path: str) -> list[tuple[str, str]]:
    pages = extract_pages(pdf_path)
    sections = split_into_sections(pages)

    result: list[tuple[str, str]] = []

    for section_name, text in sections:
        sub_chunks = _split_long_text(text)
        merged: list[str] = []
        for sub_chunk in sub_chunks:
            if merged and len(sub_chunk) < MIN_CHUNK_CHAR:
                merged[-1] = f"{merged[-1]}\n\n{sub_chunk}".strip()
            else:
                merged.append(sub_chunk)
        for chunk_text in merged:
            if chunk_text.strip():
                result.append((section_name, chunk_text))
    return result
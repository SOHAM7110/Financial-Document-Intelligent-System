""" download financial-report PDFs and 
verify whether they've already been downloaded."""

import hashlib
from pathlib import Path
import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    "(KHTML, like Gecko) Chrom/124.0 Safari/537.36"
)

TIMEOUT_SECONDS = 30

"""
you're making the request look like it comes from a normal web browser (Chrome on Windows)
rather than a simple Python script.

Why is it used?
Some websites may Block requests that don't have a recognizable User-Agent
Treat requests differently based on the client and Reject automated requests that look suspicious

So this Python script → Website is presented more like Chrome browser → Website
"""

def download_pdf(url: str, dest_path: str) -> tuple[str, int]:
    """
    Downloads url to dest_path
    Returns (sha256_hash, byte_size)
    Raises requests.HTTPError on non-200 responses -- caller is responsible
    for catching this and calling db.mark_failed()
    """
    Path(dest_path).parent.mkdir(parents = True, exist_ok = True)
    response = requests.get(
        url, headers = {"User-Agent" : USER_AGENT}, timeout = TIMEOUT_SECONDS, stream = True
    )
    response.raise_for_status()

    hasher = hashlib.sha256()
    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunki_size = 8192):
            f.write(chunk)
            hasher.update(chunk)
    return hasher.hexdigest(), Path(dest_path).stat().st_size

def already_downloaded(existing_hash: str | None, new_hash: str) -> bool:
    return existing_hash is not None and existing_hash == new_hash
from src.config import Company

ANNUAL_REPORT_URLS: dict[str, list[str]] = {}
TRANSSCRIPT_URLS: dict[str, list[str]] = {}

def get_document_urls(company : Company) -> list[tuple[str, str]]:
    urls: list[tuple[str, str]] = []
    for url in ANNUAL_REPORT_URLS.get(company.nse_symbol, []):
        urls.append(("annual_report", url))
    for url in TRANSSCRIPT_URLS.get(company.nse_symbol, []):
        urls.append(("transcript", url))
    return urls
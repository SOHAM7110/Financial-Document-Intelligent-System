# DEMO ANNUAL REPORT PDF
# Purely for testing

import fitz

def build_sample_annual_report(output_path: str) -> None:
    doc = fitz.open()
    sections = {
        "Chairman's Letter": (
            "Dear Shareholders,\n\n"
            "It gives me great pleasure to present the annual report for the "
            "financial year. Our company delivered strong performance across "
            "all business segments despite a challenging macroeconomic "
            "environment.\n\n"
            "Revenue grew by 14.2% year-on-year to Rs. 45,320 crore, while "
            "net profit increased by 9.8% to Rs. 6,120 crore. We remain "
            "committed to sustainable growth and shareholder value creation."
        ),
        "Management Discussion And Analysis": (
            "The Indian economy showed resilience during the year under "
            "review. Our EBITDA margin improved to 22.4% in Q4FY25, up from "
            "20.1% in the previous corresponding quarter. This improvement "
            "was driven primarily by operational efficiencies and better "
            "product mix.\n\n"
            "Segment-wise, our banking and financial services vertical grew "
            "18% while the retail segment grew 11%. We expect this momentum "
            "to continue into the next fiscal year, supported by strong "
            "order books and improving demand conditions across key markets."
        ),
        "Risk Factors": (
            "Our business is subject to various risks including regulatory "
            "changes by SEBI and RBI, currency fluctuation risk, and credit "
            "risk in our lending portfolio. Any adverse regulatory action "
            "could materially impact our operations.\n\n"
            "We have implemented a comprehensive risk management framework "
            "to identify, assess, and mitigate these risks on an ongoing "
            "basis, overseen directly by the Risk Management Committee of "
            "the Board."
        ),
        "Financial Highlights": (
            "Total Income: Rs. 48,900 crore\n"
            "Net Profit: Rs. 6,120 crore\n"
            "EPS: Rs. 82.40\n"
            "Return on Equity: 16.8%\n"
            "Debt to Equity Ratio: 0.42"
        ),
    }

    for heading, body in sections.items():
        page = doc.new_page()
        page.insert_text((72, 72), heading, fontsize = 14)
        page.insert_text((72, 110), body, fontsize = 10)

    doc.save(output_path)
    doc.close()

def main():
    build_sample_annual_report("data/raw/_sample_annual_report.pdf")
    print("Sample PDF written to data/raw/_sample_annual_report.pdf")
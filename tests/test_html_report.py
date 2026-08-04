import os
import pytest
from pathlib import Path
from html.parser import HTMLParser
from solarscan.cli import run_scan

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_HTML = ROOT / "sample-report.html"

class HTMLReportParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.local_urls = []
        self.inline_handlers = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name.startswith("on"):
                self.inline_handlers.append((tag, name))
            if name in {"href", "src"} and value:
                if not value.startswith(("http://", "https://", "#", "mailto:", "data:")):
                    self.local_urls.append(value)


def test_sample_report_html_structure_and_metrics():
    assert SAMPLE_HTML.exists()
    html_content = SAMPLE_HTML.read_text(encoding="utf-8")

    parser = HTMLReportParser()
    parser.feed(html_content)

    assert parser.inline_handlers == []
    missing_assets = [url for url in parser.local_urls if not (ROOT / url).exists()]
    assert missing_assets == []

    # Check reference values from W5 engine calculation
    assert "1,361.92 m²" in html_content
    assert "272.38 kW DC" in html_content
    assert "226.99 kW AC" in html_content
    assert "3.08 years" in html_content


def test_pdf_and_html_report_data_parity(tmp_path, monkeypatch):
    captured_data = []

    def mock_pdf(report_data, out_path):
        captured_data.append(("pdf", report_data))
        Path(out_path).write_bytes(b"%PDF-1.4\n% mock\n")

    def mock_html(report_data, out_path):
        captured_data.append(("html", report_data))
        Path(out_path).write_text("<html>mock</html>", encoding="utf-8")

    monkeypatch.setattr("solarscan.cli.generate_pdf_report", mock_pdf)
    monkeypatch.setattr("solarscan.cli.generate_html_report", mock_html)

    run_scan(
        address="Test Parity Address",
        fixture_path="fixtures/w5_demo.json",
        fmt="both",
        out_dir=str(tmp_path)
    )

    pdf_runs = [d for fmt_type, d in captured_data if fmt_type == "pdf"]
    html_runs = [d for fmt_type, d in captured_data if fmt_type == "html"]

    assert len(pdf_runs) == 1
    assert len(html_runs) == 1

    pdf_data = pdf_runs[0]
    html_data = html_runs[0]

    assert pdf_data["usable_area"] == html_data["usable_area"]
    assert pdf_data["dc_capacity_kw"] == html_data["dc_capacity_kw"]
    assert pdf_data["annual_kwh"] == html_data["annual_kwh"]

import os
import pytest
from pathlib import Path
from solarscan.cli import run_scan

def test_offline_demo_zero_network_and_metrics_match(tmp_path, monkeypatch):
    # Monkeypatch requests.get and requests.post to raise on call
    def raise_network_error(*args, **kwargs):
        raise RuntimeError("Network call attempted during offline demo run!")

    monkeypatch.setattr("requests.get", raise_network_error)
    monkeypatch.setattr("requests.post", raise_network_error)
    monkeypatch.setattr("solarscan.osm.requests.get", raise_network_error)
    monkeypatch.setattr("solarscan.osm.requests.post", raise_network_error)

    captured_report_data = []

    def mock_generate_pdf_report(report_data, output_pdf_path):
        captured_report_data.append(report_data)
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
        Path(output_pdf_path).write_bytes(b"%PDF-1.4\n% mock demo pdf\n")

    monkeypatch.setattr("solarscan.cli.generate_pdf_report", mock_generate_pdf_report)

    fixture_path = "fixtures/w5_demo.json"
    pdf_out = run_scan(
        address="Computer Science Department W5 Sharjah",
        tilt=15,
        rate_aed=0.38,
        out_dir=str(tmp_path),
        fixture_path=fixture_path
    )

    assert os.path.exists(pdf_out)
    assert len(captured_report_data) == 1

    data = captured_report_data[0]

    # Reference values from test_landing_page.py
    assert data["usable_area"] == pytest.approx(1361.92, abs=0.1)
    assert data["dc_capacity_kw"] == pytest.approx(272.384, abs=0.1)
    assert data["ac_capacity_kw"] == pytest.approx(226.99, abs=0.1)
    assert data["annual_kwh"] == pytest.approx(232394.62, abs=10.0)

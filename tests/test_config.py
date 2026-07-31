import pytest
import os
from pathlib import Path
import yaml
from solarscan.cli import load_config, run_scan

def test_config_defaults(tmp_path):
    config_file = tmp_path / "solarscan.yaml"
    config_file.write_text("default_tilt_deg: 15\nsetback_m: 1.5\nmodule_efficiency: 0.20\ndc_ac_ratio: 1.2\n")
    
    cfg = load_config(str(config_file))
    assert cfg["default_tilt_deg"] == 15
    assert cfg["setback_m"] == 1.5
    assert cfg["module_efficiency"] == 0.20
    assert cfg["dc_ac_ratio"] == 1.2

def test_config_behavior_change(tmp_path, monkeypatch):
    generated_reports = []

    def capture_report(report_data, output_pdf_path):
        generated_reports.append(report_data)
        Path(output_pdf_path).write_bytes(b"%PDF-1.4\n% deterministic test fixture\n")

    monkeypatch.setattr("solarscan.cli.generate_pdf_report", capture_report)

    # Default run with setback 1.5
    cfg_default = tmp_path / "cfg1.yaml"
    cfg_default.write_text("setback_m: 1.5\nmodule_efficiency: 0.20\n")
    
    pdf1 = run_scan("Test Addr 1", out_dir=str(tmp_path), config_path=str(cfg_default))
    assert os.path.exists(pdf1)
    
    # Run with larger setback 5.0
    cfg_modified = tmp_path / "cfg2.yaml"
    cfg_modified.write_text("setback_m: 5.0\nmodule_efficiency: 0.20\n")
    
    pdf2 = run_scan("Test Addr 2", out_dir=str(tmp_path), config_path=str(cfg_modified))
    assert os.path.exists(pdf2)
    assert len(generated_reports) == 2
    assert generated_reports[1]["usable_area"] < generated_reports[0]["usable_area"]
    assert generated_reports[1]["dc_capacity_kw"] < generated_reports[0]["dc_capacity_kw"]

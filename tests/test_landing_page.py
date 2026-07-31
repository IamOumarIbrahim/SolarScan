from html.parser import HTMLParser
from pathlib import Path

import pytest

from solarscan.geometry import calculate_usable_area
from solarscan.sizing import calculate_dc_capacity, recommend_inverter_capacity
from solarscan.yield_estimate import estimate_annual_yield, estimate_simple_payback


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


class LandingPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.local_urls = []
        self.inline_handlers = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.append(attributes["id"])

        for name, value in attrs:
            if name.startswith("on"):
                self.inline_handlers.append((tag, name))
            if name in {"href", "src"} and value:
                if not value.startswith(("http://", "https://", "#", "mailto:", "data:")):
                    self.local_urls.append(value)


@pytest.fixture(scope="module")
def parsed_page():
    parser = LandingPageParser()
    parser.feed(INDEX.read_text(encoding="utf-8"))
    return parser


def test_landing_page_local_assets_exist(parsed_page):
    missing = [url for url in parsed_page.local_urls if not (ROOT / url).exists()]
    assert missing == []


def test_landing_page_has_unique_ids_and_no_inline_handlers(parsed_page):
    assert len(parsed_page.ids) == len(set(parsed_page.ids))
    assert parsed_page.inline_handlers == []


def test_landing_page_uses_hardened_local_assets():
    html = INDEX.read_text(encoding="utf-8")
    assert "default-src 'self'" in html
    assert "script-src 'self'" in html
    assert "style-src 'self'" in html
    assert "unsafe-inline" not in html
    assert "assets/site.css" in html
    assert "assets/site.js" in html
    assert "assets/og-solarscan.png" in html


def test_landing_page_quickstart_matches_cli_contract():
    html = INDEX.read_text(encoding="utf-8")
    assert "python -m pip install -e ." in html
    assert 'solarscan scan "Computer Science Department W5 Sharjah"' in html
    assert 'python -m solarscan "Computer Science Department W5 Sharjah"' not in html


def test_w5_landing_page_metrics_match_engine():
    raw_area = 1610.02
    perimeter = 165.4
    usable_area = calculate_usable_area(raw_area, perimeter, setback_m=1.5)
    dc_capacity = calculate_dc_capacity(usable_area, module_efficiency=0.20)
    ac_capacity = recommend_inverter_capacity(dc_capacity, dc_ac_ratio=1.2)
    annual_yield = estimate_annual_yield(
        dc_capacity,
        tilt_deg=15,
        azimuth_deg=303.8,
    )
    payback = estimate_simple_payback(
        annual_yield,
        rate_per_kwh=0.38,
        dc_capacity_kw=dc_capacity,
    )

    assert usable_area == pytest.approx(1361.92)
    assert dc_capacity == pytest.approx(272.384)
    assert ac_capacity == pytest.approx(226.99)
    assert annual_yield == pytest.approx(232394.62)
    assert payback == pytest.approx(3.08)

    html = INDEX.read_text(encoding="utf-8")
    assert "1,361.92 m²" in html
    assert "272.38 kW" in html
    assert "226.99 kW" in html
    assert "232,395 kWh/yr" in html
    assert "3.08 years" in html


def test_case_study_ratio_is_labeled_not_generalized():
    html = INDEX.read_text(encoding="utf-8")
    ratio = 1610.02 / 1699.86 * 100
    difference = (1699.86 - 1610.02) / 1699.86 * 100

    assert ratio == pytest.approx(94.715, abs=0.001)
    assert difference == pytest.approx(5.285, abs=0.001)
    assert "94.7%" in html
    assert "5.3%" in html
    assert "one documented comparison" in html
    assert "94.7% Agreement" not in html

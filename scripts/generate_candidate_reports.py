import csv
import os
from solarscan.cli import run_scan

def main():
    dataset_path = "validation/dataset.csv"
    out_dir = "reports/validation_reports"
    os.makedirs(out_dir, exist_ok=True)

    with open(dataset_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Generating PDF & HTML reports for {len(rows)} candidates into '{out_dir}'...")
    for idx, r in enumerate(rows, 1):
        cid = r["id"]
        addr = r["address"]
        fixture_path = f"validation/fixtures/{cid}.json"
        print(f"[{idx}/{len(rows)}] Generating report for {cid} ('{addr}')...")
        run_scan(
            address=addr,
            fixture_path=fixture_path,
            fmt="both",
            out_dir=out_dir
        )

    print(f"\nSuccessfully generated reports for all {len(rows)} candidates in '{out_dir}'.")

if __name__ == "__main__":
    main()

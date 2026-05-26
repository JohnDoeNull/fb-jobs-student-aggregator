from __future__ import annotations

import argparse
from pathlib import Path

from src.collectors.facebook_collector import FacebookCollector
from src.pipeline.classifier import enrich_jobs
from src.pipeline.storage import save_csv, save_json


def run_pipeline(config_path: str) -> None:
    collector = FacebookCollector(config_path)
    raw_jobs = collector.collect()
    jobs = enrich_jobs(raw_jobs)

    out_json = Path("data/processed/jobs.json")
    out_csv = Path("data/processed/jobs.csv")

    save_json(out_json, jobs)
    save_csv(out_csv, jobs)

    print(f"Processed {len(jobs)} jobs")
    print(f"JSON: {out_json}")
    print(f"CSV : {out_csv}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run_pipeline(args.config)


if __name__ == "__main__":
    main()

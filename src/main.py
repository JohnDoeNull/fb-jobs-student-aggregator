import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = Path(args.config)
    if not cfg.exists():
        raise FileNotFoundError(f"Config not found: {cfg}")

    print("[stub] Start collecting jobs from Facebook groups...")
    print(f"Using config: {cfg}")
    print("[stub] TODO: implement collectors + pipeline")


if __name__ == "__main__":
    main()

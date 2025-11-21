"""Main entry point for the transcript ETL pipeline."""

import sys

from transcript_etl_pipeline.cli import main as cli_main


def main() -> None:
    """Main entry point that delegates to CLI."""
    sys.exit(cli_main())


if __name__ == "__main__":
    main()

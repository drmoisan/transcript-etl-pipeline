"""Main entry point for the transcript ETL pipeline."""

import sys

from transcript_etl_pipeline.cli import main as cli_main

# from transcript_etl_pipeline.devtools.debug_callgraph import run_with_callgraph


def main() -> None:
    """Main entry point that delegates to CLI."""
    # run_with_callgraph(cli_main)
    sys.exit(cli_main())


if __name__ == "__main__":
    main()

"""Command-line interface for the transcript ETL pipeline.

This module provides a CLI for running the complete transcript ETL pipeline:
extract → transform → load.
"""

import argparse
import traceback
from datetime import datetime
from pathlib import Path

from transcript_etl_pipeline import config
from transcript_etl_pipeline.devtools.debug_callgraph import run_with_callgraph
from transcript_etl_pipeline.document.parser import parse_enhanced_text
from transcript_etl_pipeline.extract.from_clipboard import extract_from_clipboard
from transcript_etl_pipeline.extract.from_file import extract_from_file
from transcript_etl_pipeline.formatters.docx_formatter import format_to_docx
from transcript_etl_pipeline.formatters.md_formatter import format_to_md
from transcript_etl_pipeline.formatters.rtf_formatter import format_to_rtf
from transcript_etl_pipeline.logging_config import get_logger, setup_logging
from transcript_etl_pipeline.transform.enhance import enhance_text
from transcript_etl_pipeline.transform.normalize import normalize_text
from transcript_etl_pipeline.transform.speakers import SpeakerResolutionUI

logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="transcript-etl",
        description="Extract, transform, and format meeting transcripts",
    )

    parser.add_argument(
        "--source",
        choices=["clipboard", "file"],
        help="Source of the transcript text",
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Path to transcript file (required if --source=file)",
    )

    parser.add_argument(
        "--format",
        choices=["docx", "rtf", "md"],
        default="docx",
        help="Output format (default: docx)",
    )

    parser.add_argument(
        "--output-name",
        type=str,
        help="Name for the output file (without extension)",
    )

    parser.add_argument(
        "--output-folder",
        type=str,
        help="Folder where output file should be saved",
    )

    return parser


def generate_default_filename(format_ext: str) -> str:
    """Generate a default filename based on current date.

    Args:
        format_ext: File extension (docx, rtf, or md)

    Returns:
        Generated filename like "2024 01 15 Transcript.docx"
    """
    today = datetime.now()
    return f"{today.year} {today.month:02d} {today.day:02d} Transcript.{format_ext}"


def run_pipeline(
    source: str,
    file_path: str | None,
    output_format: str,
    output_name: str,
    output_folder: str,
    ui_callback: SpeakerResolutionUI | None = None,
) -> None:
    """Run the complete ETL pipeline.

    Args:
        source: Either "clipboard" or "file"
        file_path: Path to file if source is "file"
        output_format: Output format (docx, rtf, or md)
        output_name: Name for output file (with extension)
        output_folder: Folder to save output file
        ui_callback: Optional UI callback for speaker resolution

    Raises:
        ValueError: If invalid parameters are provided
        FileNotFoundError: If file path doesn't exist
        RuntimeError: If pipeline execution fails
    """
    logger.info("=" * 60)
    logger.info("STARTING TRANSCRIPT ETL PIPELINE")
    logger.info("=" * 60)
    logger.info(f"Source: {source}")
    logger.info(f"File path: {file_path}")
    logger.info(f"Output format: {output_format}")
    logger.info(f"Output name: {output_name}")
    logger.info(f"Output folder: {output_folder}")
    logger.info("-" * 60)

    # Extract
    logger.info(f"STAGE 1: EXTRACT - Reading from {source}")
    print(f"Extracting from {source}...")
    try:
        if source == "clipboard":
            logger.debug("Calling extract_from_clipboard()")
            raw_text = extract_from_clipboard()
        elif source == "file":
            if not file_path:
                raise ValueError("--file is required when --source=file")
            logger.debug(f"Calling extract_from_file({file_path})")
            raw_text = extract_from_file(file_path)
        else:
            raise ValueError(f"Invalid source: {source}")

        logger.info(f"✓ Extracted {len(raw_text)} characters")
        logger.debug(f"First 200 chars: {raw_text[:200]!r}")
        logger.info("-" * 60)
    except Exception as e:
        logger.error(f"✗ EXTRACT FAILED: {type(e).__name__}: {e}")
        logger.debug(traceback.format_exc())
        raise

    # Transform - Normalize
    logger.info("STAGE 2: NORMALIZE - Cleaning text")
    print("Normalizing text...")
    try:
        logger.debug("Calling normalize_text()")
        normalized_text = normalize_text(raw_text)
        logger.info(f"✓ Normalized to {len(normalized_text)} characters")
        logger.debug(f"First 200 chars: {normalized_text[:200]!r}")
        logger.info("-" * 60)
    except Exception as e:
        logger.error(f"✗ NORMALIZE FAILED: {type(e).__name__}: {e}")
        logger.debug(traceback.format_exc())
        raise

    # Transform - Enhance
    logger.info("STAGE 3: ENHANCE - Detecting paragraphs and speakers")
    print("Enhancing text (paragraphs, speakers)...")
    try:
        logger.debug("Calling enhance_text()")
        enhanced_text, speaker_map = enhance_text(normalized_text, ui_callback=ui_callback)
        logger.info(f"✓ Enhanced to {len(enhanced_text)} characters")
        logger.info(f"✓ Identified {len(speaker_map)} speakers: {speaker_map}")
        logger.debug(f"First 200 chars: {enhanced_text[:200]!r}")
        print(f"Identified speakers: {speaker_map if speaker_map else 'None'}")
        logger.info("-" * 60)
    except Exception as e:
        logger.error(f"✗ ENHANCE FAILED: {type(e).__name__}: {e}")
        logger.debug(traceback.format_exc())
        raise

    # Parse enhanced text into Document model
    logger.info("STAGE 4: PARSE - Building document structure")
    print("Parsing document structure...")
    try:
        logger.debug("Calling parse_enhanced_text()")
        document = parse_enhanced_text(enhanced_text)
        logger.info(f"✓ Parsed document with {len(document.sections)} sections")
        for i, section in enumerate(document.sections):
            logger.debug(
                f"  Section {i+1}: {
                    section.section_type.value
                }, {len(section.paragraphs)} paragraphs"
            )
        logger.info("-" * 60)
    except Exception as e:
        logger.error(f"✗ PARSE FAILED: {type(e).__name__}: {e}")
        logger.debug(traceback.format_exc())
        raise

    # Load - Format and save
    logger.info(f"STAGE 5: LOAD - Formatting to {output_format.upper()}")
    print(f"Formatting to {output_format.upper()}...")
    try:
        output_path = Path(output_folder) / output_name
        logger.debug(f"Output path: {output_path}")

        # Format based on output format
        if output_format == "docx":
            logger.debug("Calling format_to_docx()")
            format_to_docx(document, str(output_path))
        elif output_format == "rtf":
            logger.debug("Calling format_to_rtf()")
            format_to_rtf(document, str(output_path))
        elif output_format == "md":
            logger.debug("Calling format_to_md()")
            format_to_md(document, str(output_path))
        else:
            raise ValueError(f"Unsupported format: {output_format}")

        logger.info(f"✓ Output saved to: {output_path}")
        print(f"✓ Output saved to: {output_path}")
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"✗ LOAD FAILED: {type(e).__name__}: {e}")
        logger.debug(traceback.format_exc())
        raise

    # Save the output folder to config
    config.save_last_output_folder(output_folder)


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        args: Command-line arguments (defaults to sys.argv if None)

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Set up logging first thing
    # log_file = Path.home() / "artifacts" / "pipeline.log"
    log_file = Path(__file__).resolve().parents[2] / "artifacts" / "pipeline.log"
    setup_logging(str(log_file))
    logger.info("Transcript ETL Pipeline starting...")

    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Validate arguments
    source = parsed_args.source
    file_path = parsed_args.file
    output_format = parsed_args.format
    output_name = parsed_args.output_name
    output_folder = parsed_args.output_folder

    logger.debug(
        f"Parsed arguments: source={source}, file={file_path}, "
        + f"format={output_format}, name={output_name}, folder={output_folder}"
    )

    # Try to use UI for missing arguments
    from transcript_etl_pipeline.transform.speakers import SpeakerResolutionUI

    ui_callback: SpeakerResolutionUI | None = None
    use_ui = not all([source, output_folder])

    logger.debug(f"Use UI: {use_ui}")

    if use_ui:
        try:
            logger.debug("Importing UI module")
            from transcript_etl_pipeline import ui

            # Prompt for source if missing
            if not source:
                logger.debug("Prompting for source selection")
                source = ui.prompt_source_selection()
                if not source:
                    logger.warning("User cancelled source selection")
                    print("Operation cancelled by user.")
                    return 1

            # Prompt for file if source is file and file_path is missing
            if source == "file" and not file_path:
                logger.debug("Prompting for file selection")
                file_path = ui.prompt_file_selection()
                if not file_path:
                    logger.warning("User cancelled file selection")
                    print("Operation cancelled by user.")
                    return 1

            # Prompt for format if not specified (though it has a default)
            if not parsed_args.format:
                logger.debug("Prompting for format selection")
                fmt = ui.prompt_format_selection()
                if not fmt:
                    logger.warning("User cancelled format selection")
                    print("Operation cancelled by user.")
                    return 1
                output_format = fmt

            # Generate default filename if not provided
            if not output_name:
                default_name = generate_default_filename(output_format)
                logger.debug(f"Generated default filename: {default_name}")
                output_name = ui.prompt_output_name(default_name)
                if not output_name:
                    logger.warning("User cancelled output name selection")
                    print("Operation cancelled by user.")
                    return 1

            # Prompt for output folder if missing
            if not output_folder:
                last_folder = config.load_last_output_folder()
                logger.debug(f"Last output folder: {last_folder}")
                output_folder = ui.prompt_output_folder(last_folder)
                if not output_folder:
                    logger.warning("User cancelled output folder selection")
                    print("Operation cancelled by user.")
                    return 1

            # Create UI callback for speaker resolution
            logger.debug("Creating speaker resolution UI callback")
            ui_callback = ui.create_speaker_resolution_callback()

        except RuntimeError as e:
            logger.error(f"UI initialization failed: {e}")
            logger.debug(traceback.format_exc())
            print(f"Error: {e}")
            print("Please provide all required CLI arguments.")
            parser.print_help()
            return 1

    # If not using UI, check for missing required args
    if not use_ui:
        missing_args: list[str] = []

        if not source:
            missing_args.append("--source")

        if source == "file" and not file_path:
            missing_args.append("--file (required when --source=file)")

        if not output_name:
            # Generate default filename
            output_name = generate_default_filename(output_format)
            logger.info(f"Using default filename: {output_name}")
            print(f"Using default filename: {output_name}")

        if not output_folder:
            # Try to use last folder from config
            last_folder = config.load_last_output_folder()
            if last_folder:
                output_folder = last_folder
                logger.info(f"Using last output folder: {output_folder}")
                print(f"Using last output folder: {output_folder}")
            else:
                missing_args.append("--output-folder")

        # If any required args are missing, show error
        if missing_args:
            logger.error(f"Missing required arguments: {missing_args}")
            print(f"Error: Missing required arguments: {', '.join(missing_args)}")
            parser.print_help()
            return 1

    # Validate file path if provided
    if source == "file" and file_path and not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        print(f"Error: File not found: {file_path}")
        return 1

    # Validate output folder
    if output_folder:
        output_dir = Path(output_folder)
        if not output_dir.exists():
            logger.error(f"Output folder does not exist: {output_folder}")
            print(f"Error: Output folder does not exist: {output_folder}")
            return 1
        if not output_dir.is_dir():
            logger.error(f"Output folder is not a directory: {output_folder}")
            print(f"Error: Output folder is not a directory: {output_folder}")
            return 1

    # Run the pipeline
    try:
        logger.info("Starting pipeline execution...")
        run_pipeline(
            source=source,
            file_path=file_path,
            output_format=output_format,
            output_name=output_name,
            output_folder=output_folder,
            ui_callback=ui_callback,
        )
        logger.info("Pipeline completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"PIPELINE FAILED: {type(e).__name__}: {e}")
        logger.debug(traceback.format_exc())
        print(f"Error: {e}")
        print(f"\nFor detailed diagnostics, see log file: {log_file}")
        return 1


if __name__ == "__main__":
    run_with_callgraph(main)
    # sys.exit(run_with_callgraph(main))
    # sys.exit(main())

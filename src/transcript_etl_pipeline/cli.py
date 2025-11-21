"""Command-line interface for the transcript ETL pipeline.

This module provides a CLI for running the complete transcript ETL pipeline:
extract → transform → load.
"""

import argparse
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from transcript_etl_pipeline import config
from transcript_etl_pipeline.extract.from_clipboard import extract_from_clipboard
from transcript_etl_pipeline.extract.from_file import extract_from_file
from transcript_etl_pipeline.transform.enhance import enhance_text
from transcript_etl_pipeline.transform.normalize import normalize_text


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
    ui_callback: Callable[[str, list[str]], dict[str, str]] | None = None,
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
    # Extract
    print(f"Extracting from {source}...")
    if source == "clipboard":
        raw_text = extract_from_clipboard()
    elif source == "file":
        if not file_path:
            raise ValueError("--file is required when --source=file")
        raw_text = extract_from_file(file_path)
    else:
        raise ValueError(f"Invalid source: {source}")

    # Transform - Normalize
    print("Normalizing text...")
    normalized_text = normalize_text(raw_text)

    # Transform - Enhance
    print("Enhancing text (paragraphs, speakers)...")
    enhanced_text, speaker_map = enhance_text(normalized_text, ui_callback=ui_callback)

    print(f"Identified speakers: {speaker_map if speaker_map else 'None'}")

    # Load - Format and save
    print(f"Formatting to {output_format.upper()}...")

    # For now, we'll use a simple text-based document model
    # In a full implementation, we'd parse enhanced_text into a Document structure
    output_path = Path(output_folder) / output_name

    # Create a simple temporary file with the enhanced text
    # TODO: Parse enhanced_text into proper Document structure with sections/paragraphs
    # For now, just write the enhanced text
    output_path.write_text(enhanced_text, encoding="utf-8")

    print(f"✓ Output saved to: {output_path}")

    # Save the output folder to config
    config.save_last_output_folder(output_folder)


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        args: Command-line arguments (defaults to sys.argv if None)

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Validate arguments
    source = parsed_args.source
    file_path = parsed_args.file
    output_format = parsed_args.format
    output_name = parsed_args.output_name
    output_folder = parsed_args.output_folder

    # Try to use UI for missing arguments
    ui_callback: Callable[[str, list[str]], dict[str, str]] | None = None
    use_ui = not all([source, output_folder])

    if use_ui:
        try:
            from transcript_etl_pipeline import ui

            # Prompt for source if missing
            if not source:
                source = ui.prompt_source_selection()
                if not source:
                    print("Operation cancelled by user.")
                    return 1

            # Prompt for file if source is file and file_path is missing
            if source == "file" and not file_path:
                file_path = ui.prompt_file_selection()
                if not file_path:
                    print("Operation cancelled by user.")
                    return 1

            # Prompt for format if not specified (though it has a default)
            if not parsed_args.format:
                fmt = ui.prompt_format_selection()
                if not fmt:
                    print("Operation cancelled by user.")
                    return 1
                output_format = fmt

            # Generate default filename if not provided
            if not output_name:
                output_name = generate_default_filename(output_format)
                output_name = ui.prompt_output_name(output_name)
                if not output_name:
                    print("Operation cancelled by user.")
                    return 1

            # Prompt for output folder if missing
            if not output_folder:
                last_folder = config.load_last_output_folder()
                output_folder = ui.prompt_output_folder(last_folder)
                if not output_folder:
                    print("Operation cancelled by user.")
                    return 1

            # Create UI callback for speaker resolution
            ui_callback = ui.create_speaker_resolution_callback()

        except RuntimeError as e:
            print(f"Error: {e}")
            print("Please provide all required CLI arguments.")
            parser.print_help()
            return 1

    # If not using UI, check for missing required args
    if not use_ui:
        missing_args = []

        if not source:
            missing_args.append("--source")

        if source == "file" and not file_path:
            missing_args.append("--file (required when --source=file)")

        if not output_name:
            # Generate default filename
            output_name = generate_default_filename(output_format)
            print(f"Using default filename: {output_name}")

        if not output_folder:
            # Try to use last folder from config
            last_folder = config.load_last_output_folder()
            if last_folder:
                output_folder = last_folder
                print(f"Using last output folder: {output_folder}")
            else:
                missing_args.append("--output-folder")

        # If any required args are missing, show error
        if missing_args:
            print(f"Error: Missing required arguments: {', '.join(missing_args)}")
            parser.print_help()
            return 1

    # Validate file path if provided
    if source == "file" and file_path and not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        return 1

    # Validate output folder
    if output_folder:
        output_dir = Path(output_folder)
        if not output_dir.exists():
            print(f"Error: Output folder does not exist: {output_folder}")
            return 1
        if not output_dir.is_dir():
            print(f"Error: Output folder is not a directory: {output_folder}")
            return 1

    # Run the pipeline
    try:
        run_pipeline(
            source=source,
            file_path=file_path,
            output_format=output_format,
            output_name=output_name,
            output_folder=output_folder,
            ui_callback=ui_callback,
        )
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

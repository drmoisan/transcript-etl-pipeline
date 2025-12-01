"""Command-line interface for the transcript ETL pipeline.

This module provides a CLI for running the complete transcript ETL pipeline:
extract → transform → load.

Supports:
- Transcript-only processing (existing workflow)
- Notes-only processing
- Notes + Transcript combined
- Update existing documents (add/replace notes or transcript)
"""

import argparse
import traceback
from datetime import datetime
from pathlib import Path

from transcript_etl_pipeline import config
from transcript_etl_pipeline.devtools.debug_callgraph import run_with_callgraph
from transcript_etl_pipeline.document.model import Document
from transcript_etl_pipeline.document.parser import parse_enhanced_text
from transcript_etl_pipeline.document.reader import read_document
from transcript_etl_pipeline.extract.from_clipboard import extract_from_clipboard
from transcript_etl_pipeline.extract.from_file import extract_from_file
from transcript_etl_pipeline.formatters.docx_formatter import format_to_docx
from transcript_etl_pipeline.formatters.md_formatter import format_to_md
from transcript_etl_pipeline.formatters.rtf_formatter import format_to_rtf
from transcript_etl_pipeline.logging_config import get_logger, setup_logging
from transcript_etl_pipeline.transform.enhance import enhance_text
from transcript_etl_pipeline.transform.normalize import normalize_text
from transcript_etl_pipeline.transform.notes import transform_notes
from transcript_etl_pipeline.transform.speakers import SpeakerResolutionUI

logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="transcript-etl",
        description="Extract, transform, and format meeting transcripts and notes",
    )

    # Mode: new document vs update existing
    parser.add_argument(
        "--mode",
        choices=["new", "update"],
        default="new",
        help="Mode: 'new' creates a new document, 'update' modifies an existing one",
    )

    # For update mode: path to existing document
    parser.add_argument(
        "--update-file",
        type=str,
        help="Path to existing document to update (required if --mode=update)",
    )

    # For update mode: action for notes/transcript
    parser.add_argument(
        "--update-action",
        choices=["add-notes", "replace-notes", "add-transcript", "replace-transcript"],
        help="Action when updating: add or replace notes/transcript",
    )

    # Transcript source (original functionality)
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

    # Notes source
    parser.add_argument(
        "--notes-source",
        choices=["clipboard", "file"],
        help="Source of notes text (optional)",
    )

    parser.add_argument(
        "--notes-file",
        type=str,
        help="Path to notes file (required if --notes-source=file)",
    )

    parser.add_argument(
        "--notes-label",
        type=str,
        help="Label for notes header (auto-generated if not provided)",
    )

    # Output options
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


def _extract_text(source: str, file_path: str | None) -> str:
    """Extract text from the specified source.

    Args:
        source: Either "clipboard" or "file"
        file_path: Path to file if source is "file"

    Returns:
        Extracted text content

    Raises:
        ValueError: If source is "file" but no file_path provided
    """
    if source == "clipboard":
        logger.debug("Calling extract_from_clipboard()")
        return extract_from_clipboard()
    elif source == "file":
        if not file_path:
            raise ValueError("File path is required when source is 'file'")
        logger.debug(f"Calling extract_from_file({file_path})")
        return extract_from_file(file_path)
    else:
        raise ValueError(f"Invalid source: {source}")


def _save_document(document: Document, output_format: str, output_path: Path) -> None:
    """Save document to file in the specified format.

    Args:
        document: Document to save
        output_format: Format (docx, rtf, or md)
        output_path: Full path to output file
    """
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


def run_unified_pipeline(
    mode: str,
    output_format: str,
    output_name: str,
    output_folder: str,
    # Transcript options
    transcript_source: str | None = None,
    transcript_file: str | None = None,
    # Notes options
    notes_source: str | None = None,
    notes_file: str | None = None,
    notes_label: str | None = None,
    # Update options
    update_file: str | None = None,
    update_action: str | None = None,
    # UI callback
    ui_callback: SpeakerResolutionUI | None = None,
) -> None:
    """Run the unified ETL pipeline supporting notes and transcript.

    Args:
        mode: Either "new" or "update"
        output_format: Output format (docx, rtf, or md)
        output_name: Name for output file (with extension)
        output_folder: Folder to save output file
        transcript_source: Source for transcript ("clipboard" or "file")
        transcript_file: Path to transcript file
        notes_source: Source for notes ("clipboard" or "file")
        notes_file: Path to notes file
        notes_label: Label for notes header
        update_file: Path to existing file for update mode
        update_action: Action for update mode
        ui_callback: Optional UI callback for speaker resolution

    Raises:
        ValueError: If invalid parameters are provided
        FileNotFoundError: If file path doesn't exist
    """
    logger.info("=" * 60)
    logger.info("STARTING UNIFIED ETL PIPELINE")
    logger.info("=" * 60)
    logger.info(f"Mode: {mode}")
    logger.info(f"Transcript source: {transcript_source}")
    logger.info(f"Notes source: {notes_source}")
    logger.info(f"Output format: {output_format}")
    logger.info("-" * 60)

    document: Document

    if mode == "update":
        # Update existing document
        if not update_file:
            raise ValueError("--update-file is required when --mode=update")
        if not update_action:
            raise ValueError("--update-action is required when --mode=update")

        logger.info(f"Loading existing document: {update_file}")
        print(f"Loading existing document: {update_file}...")
        document = read_document(update_file)
        logger.info(f"✓ Loaded document with {len(document.sections)} sections")

        # Process based on update action
        if update_action in ("add-notes", "replace-notes"):
            if not notes_source:
                raise ValueError("--notes-source is required for notes update")
            _process_notes_update(document, notes_source, notes_file, notes_label, update_action)
        elif update_action in ("add-transcript", "replace-transcript"):
            if not transcript_source:
                raise ValueError("--source is required for transcript update")
            _process_transcript_update(
                document, transcript_source, transcript_file, update_action, ui_callback
            )
        else:
            raise ValueError(f"Invalid update action: {update_action}")
    else:
        # New document mode
        document = Document()

        # Process notes if provided
        if notes_source:
            logger.info(f"PROCESSING NOTES from {notes_source}")
            print(f"Processing notes from {notes_source}...")
            notes_text = _extract_text(notes_source, notes_file)
            notes_sections = transform_notes(notes_text, label=notes_label)
            for section in notes_sections:
                document.add_section(section)
            logger.info(f"✓ Added {len(notes_sections)} notes sections")

        # Process transcript if provided
        if transcript_source:
            logger.info(f"PROCESSING TRANSCRIPT from {transcript_source}")
            print(f"Processing transcript from {transcript_source}...")
            transcript_doc = _process_transcript(transcript_source, transcript_file, ui_callback)
            # Merge transcript sections into document
            for section in transcript_doc.sections:
                document.add_section(section)
            logger.info(f"✓ Added {len(transcript_doc.sections)} transcript sections")

    # Save the document
    output_path = Path(output_folder) / output_name
    logger.info(f"SAVING to {output_path}")
    print(f"Saving to {output_format.upper()}...")

    _save_document(document, output_format, output_path)

    logger.info(f"✓ Output saved to: {output_path}")
    print(f"✓ Output saved to: {output_path}")
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 60)

    # Save the output folder to config
    config.save_last_output_folder(output_folder)


def _process_transcript(
    source: str,
    file_path: str | None,
    ui_callback: SpeakerResolutionUI | None,
) -> Document:
    """Process transcript text through the full pipeline.

    Args:
        source: Source of transcript text
        file_path: Path to file if source is "file"
        ui_callback: UI callback for speaker resolution

    Returns:
        Processed Document
    """
    # Extract
    raw_text = _extract_text(source, file_path)
    logger.info(f"✓ Extracted {len(raw_text)} characters")

    # Normalize
    normalized_text = normalize_text(raw_text)
    logger.info(f"✓ Normalized to {len(normalized_text)} characters")

    # Enhance
    enhanced_text, speaker_map = enhance_text(normalized_text, ui_callback=ui_callback)
    logger.info(f"✓ Enhanced, identified {len(speaker_map)} speakers")
    print(f"Identified speakers: {speaker_map if speaker_map else 'None'}")

    # Parse
    document = parse_enhanced_text(enhanced_text)
    logger.info(f"✓ Parsed document with {len(document.sections)} sections")

    return document


def _process_notes_update(
    document: Document,
    source: str,
    file_path: str | None,
    label: str | None,
    action: str,
) -> None:
    """Process notes update on existing document.

    Args:
        document: Document to update
        source: Source of notes text
        file_path: Path to file if source is "file"
        label: Label for notes header
        action: Either "add-notes" or "replace-notes"
    """
    notes_text = _extract_text(source, file_path)
    notes_sections = transform_notes(notes_text, label=label)

    mode = "add" if action == "add-notes" else "replace"
    document.merge_notes(notes_sections, mode=mode)
    logger.info(f"✓ Notes {'added' if mode == 'add' else 'replaced'}")


def _process_transcript_update(
    document: Document,
    source: str,
    file_path: str | None,
    action: str,
    ui_callback: SpeakerResolutionUI | None,
) -> None:
    """Process transcript update on existing document.

    Args:
        document: Document to update
        source: Source of transcript text
        file_path: Path to file if source is "file"
        action: Either "add-transcript" or "replace-transcript"
        ui_callback: UI callback for speaker resolution
    """
    transcript_doc = _process_transcript(source, file_path, ui_callback)

    mode = "add" if action == "add-transcript" else "replace"
    document.merge_transcript(transcript_doc.sections, mode=mode)
    logger.info(f"✓ Transcript {'added' if mode == 'add' else 'replaced'}")


def run_pipeline(
    source: str,
    file_path: str | None,
    output_format: str,
    output_name: str,
    output_folder: str,
    ui_callback: SpeakerResolutionUI | None = None,
) -> None:
    """Run the complete ETL pipeline (legacy transcript-only mode).

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
    # Delegate to unified pipeline for backward compatibility
    run_unified_pipeline(
        mode="new",
        output_format=output_format,
        output_name=output_name,
        output_folder=output_folder,
        transcript_source=source,
        transcript_file=file_path,
        ui_callback=ui_callback,
    )


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        args: Command-line arguments (defaults to sys.argv if None)

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Set up logging first thing
    log_file = Path(__file__).resolve().parents[2] / "artifacts" / "pipeline.log"
    setup_logging(str(log_file))
    logger.info("Transcript ETL Pipeline starting...")

    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Extract arguments
    mode = parsed_args.mode
    update_file = parsed_args.update_file
    update_action = parsed_args.update_action
    source = parsed_args.source
    file_path = parsed_args.file
    notes_source = parsed_args.notes_source
    notes_file = parsed_args.notes_file
    notes_label = parsed_args.notes_label
    output_format = parsed_args.format
    output_name = parsed_args.output_name
    output_folder = parsed_args.output_folder

    logger.debug(
        f"Parsed arguments: mode={mode}, source={source}, notes_source={notes_source}, "
        + f"format={output_format}, name={output_name}, folder={output_folder}"
    )

    # Determine if we need to prompt UI for source
    has_source = (source is not None) or (notes_source is not None)
    use_ui = not has_source or not output_folder

    # Try to import UI module
    from transcript_etl_pipeline.transform.speakers import SpeakerResolutionUI

    ui_callback: SpeakerResolutionUI | None = None
    ui_module_available = False
    ui_module = None

    try:
        logger.debug("Importing UI module")
        from transcript_etl_pipeline import ui as ui_module

        ui_module_available = True

        # Only prompt for missing CLI arguments if use_ui is True
        if use_ui:
            # For new mode without any source, prompt for transcript source
            if mode == "new" and not source and not notes_source:
                logger.debug("Prompting for source selection")
                source = ui_module.prompt_source_selection()
                if not source:
                    logger.warning("User cancelled source selection")
                    print("Operation cancelled by user.")
                    return 1

            # Prompt for file if source is file and file_path is missing
            if source == "file" and not file_path:
                logger.debug("Prompting for file selection")
                file_path = ui_module.prompt_file_selection()
                if not file_path:
                    logger.warning("User cancelled file selection")
                    print("Operation cancelled by user.")
                    return 1

            # Prompt for notes file if notes_source is file and notes_file is missing
            if notes_source == "file" and not notes_file:
                logger.debug("Prompting for notes file selection")
                notes_file = ui_module.prompt_file_selection()
                if not notes_file:
                    logger.warning("User cancelled notes file selection")
                    print("Operation cancelled by user.")
                    return 1

            # Generate default filename if not provided
            if not output_name:
                default_name = generate_default_filename(output_format)
                logger.debug(f"Generated default filename: {default_name}")
                output_name = ui_module.prompt_output_name(default_name)
                if not output_name:
                    logger.warning("User cancelled output name selection")
                    print("Operation cancelled by user.")
                    return 1

            # Prompt for output folder if missing
            if not output_folder:
                last_folder = config.load_last_output_folder()
                logger.debug(f"Last output folder: {last_folder}")
                output_folder = ui_module.prompt_output_folder(last_folder)
                if not output_folder:
                    logger.warning("User cancelled output folder selection")
                    print("Operation cancelled by user.")
                    return 1

    except RuntimeError as e:
        logger.error(f"UI initialization failed: {e}")
        logger.debug(traceback.format_exc())
        if use_ui:
            print(f"Error: {e}")
            print("Please provide all required CLI arguments.")
            parser.print_help()
            return 1
        else:
            logger.warning(f"UI unavailable for speaker resolution: {e}")
            logger.info("Speaker resolution will be skipped if auto-detect fails")
            ui_module_available = False
            ui_module = None

    # Create UI callback lazily
    if ui_module_available and ui_module is not None:
        logger.debug("UI module available for speaker resolution")
        ui_callback = ui_module.create_speaker_resolution_callback()
    else:
        logger.debug("UI module not available - speaker resolution will use auto-detection only")

    # Validate arguments based on mode
    if mode == "update":
        if not update_file:
            print("Error: --update-file is required when --mode=update")
            return 1
        if not update_action:
            print("Error: --update-action is required when --mode=update")
            return 1
        if not Path(update_file).exists():
            print(f"Error: Update file not found: {update_file}")
            return 1

    # If not using UI, check for missing required args
    if not use_ui:
        if not output_name:
            output_name = generate_default_filename(output_format)
            logger.info(f"Using default filename: {output_name}")
            print(f"Using default filename: {output_name}")

        if not output_folder:
            last_folder = config.load_last_output_folder()
            if last_folder:
                output_folder = last_folder
                logger.info(f"Using last output folder: {output_folder}")
                print(f"Using last output folder: {output_folder}")
            else:
                print("Error: --output-folder is required")
                parser.print_help()
                return 1

    # Validate file paths
    if source == "file" and file_path and not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        print(f"Error: File not found: {file_path}")
        return 1

    if notes_source == "file" and notes_file and not Path(notes_file).exists():
        logger.error(f"Notes file not found: {notes_file}")
        print(f"Error: Notes file not found: {notes_file}")
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

    # At this point, ensure required values are set
    assert output_name is not None, "output_name must be set"
    assert output_folder is not None, "output_folder must be set"

    # Run the pipeline
    try:
        logger.info("Starting pipeline execution...")
        run_unified_pipeline(
            mode=mode,
            output_format=output_format,
            output_name=output_name,
            output_folder=output_folder,
            transcript_source=source,
            transcript_file=file_path,
            notes_source=notes_source,
            notes_file=notes_file,
            notes_label=notes_label,
            update_file=update_file,
            update_action=update_action,
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

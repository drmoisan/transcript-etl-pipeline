"""User interface dialogs for the transcript ETL pipeline.

This module provides tkinter-based dialogs for user interaction when
CLI arguments are not provided.
"""

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog

# Try to import tkinter at runtime
try:
    import tkinter as tk  # type: ignore[no-redef]
    from tkinter import filedialog, messagebox, simpledialog  # type: ignore[no-redef]

    _tkinter_available = True
except ImportError:
    _tkinter_available = False
    # Create dummy placeholders to avoid "possibly unbound" errors
    tk = None  # type: ignore[assignment]
    filedialog = None  # type: ignore[assignment]
    messagebox = None  # type: ignore[assignment]
    simpledialog = None  # type: ignore[assignment]


def check_tkinter_available() -> None:
    """Check if tkinter is available and raise an error if not.

    Raises:
        RuntimeError: If tkinter is not available
    """
    if not _tkinter_available:
        raise RuntimeError("tkinter is not available. Please provide all required CLI arguments.")


def show_error(title: str, message: str) -> None:
    """Show an error dialog.

    Args:
        title: Dialog title
        message: Error message
    """
    check_tkinter_available()
    if tk is None or messagebox is None:
        raise RuntimeError("tkinter is not available")
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title, message)
    root.destroy()


def show_info(title: str, message: str) -> None:
    """Show an informational dialog.

    Args:
        title: Dialog title
        message: Information message
    """
    check_tkinter_available()
    if tk is None or messagebox is None:
        raise RuntimeError("tkinter is not available")
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)
    root.destroy()


def prompt_source_selection() -> str | None:
    """Prompt user to select transcript source.

    Returns:
        "clipboard", "file", or None if cancelled
    """
    check_tkinter_available()
    assert tk is not None and messagebox is not None

    root = tk.Tk()
    root.withdraw()

    result = messagebox.askquestion(
        "Transcript Source",
        "Select transcript source:\n\nYes = Clipboard\nNo = File",
        icon="question",
    )

    root.destroy()

    if result == "yes":
        return "clipboard"
    elif result == "no":
        return "file"
    else:
        return None


def prompt_file_selection() -> str | None:
    """Prompt user to select a transcript file.

    Returns:
        Path to selected file, or None if cancelled
    """
    check_tkinter_available()
    assert tk is not None and filedialog is not None

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select Transcript File",
        filetypes=[
            ("Text files", "*.txt"),
            ("Markdown files", "*.md"),
            ("All files", "*.*"),
        ],
    )

    root.destroy()

    return file_path if file_path else None


def prompt_format_selection() -> str | None:
    """Prompt user to select output format.

    Returns:
        "docx", "rtf", "md", or None if cancelled
    """
    check_tkinter_available()
    assert tk is not None

    root = tk.Tk()
    root.withdraw()

    # Create a simple dialog for format selection
    dialog = tk.Toplevel(root)
    dialog.title("Select Output Format")
    dialog.geometry("300x150")

    result: dict[str, str | None] = {"format": None}

    tk.Label(dialog, text="Select output format:", font=("Arial", 12)).pack(pady=10)

    def on_format_selected(fmt: str) -> None:
        result["format"] = fmt
        dialog.destroy()

    tk.Button(
        dialog, text="DOCX (Microsoft Word)", command=lambda: on_format_selected("docx"), width=25
    ).pack(pady=5)
    tk.Button(
        dialog, text="RTF (Rich Text Format)", command=lambda: on_format_selected("rtf"), width=25
    ).pack(pady=5)
    tk.Button(
        dialog, text="MD (Markdown)", command=lambda: on_format_selected("md"), width=25
    ).pack(pady=5)

    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)
    root.destroy()

    return result["format"]


def prompt_output_name(default_name: str) -> str | None:
    """Prompt user to enter output filename.

    Args:
        default_name: Default filename to suggest

    Returns:
        Filename entered by user, or None if cancelled
    """
    check_tkinter_available()
    assert tk is not None and simpledialog is not None

    root = tk.Tk()
    root.withdraw()

    name = simpledialog.askstring(
        "Output Filename", "Enter output filename:", initialvalue=default_name
    )

    root.destroy()

    return name if name else None


def prompt_output_folder(default_folder: str | None = None) -> str | None:
    """Prompt user to select output folder.

    Args:
        default_folder: Default folder to start in

    Returns:
        Path to selected folder, or None if cancelled
    """
    check_tkinter_available()
    assert tk is not None and filedialog is not None

    root = tk.Tk()
    root.withdraw()

    initial_dir = default_folder if default_folder and Path(default_folder).exists() else None

    folder_path = filedialog.askdirectory(title="Select Output Folder", initialdir=initial_dir)

    root.destroy()

    return folder_path if folder_path else None


def prompt_speaker_mapping(speaker_label: str, samples: list[str]) -> str | None:
    """Prompt user to map a speaker label to a person's name.

    Args:
        speaker_label: The speaker label to map (e.g., "Speaker A")
        samples: Sample utterances from this speaker

    Returns:
        Person's name, or None if cancelled
    """
    check_tkinter_available()
    assert tk is not None

    root = tk.Tk()
    root.withdraw()

    # Create dialog
    dialog = tk.Toplevel(root)
    dialog.title(f"Identify {speaker_label}")
    dialog.geometry("500x400")

    tk.Label(dialog, text=f"Who is {speaker_label}?", font=("Arial", 12, "bold")).pack(pady=10)

    tk.Label(dialog, text="Sample utterances:", font=("Arial", 10)).pack(pady=5)

    # Show samples in a text box
    text_box = tk.Text(dialog, height=10, width=60, wrap=tk.WORD)
    text_box.pack(pady=5, padx=10)

    for i, sample in enumerate(samples[:3], 1):
        text_box.insert(tk.END, f"{i}. {sample}\n\n")

    text_box.config(state=tk.DISABLED)

    # Name entry
    tk.Label(dialog, text="Enter person's name:", font=("Arial", 10)).pack(pady=5)
    name_entry = tk.Entry(dialog, width=40)
    name_entry.pack(pady=5)
    name_entry.focus()

    result: dict[str, str | None] = {"name": None}

    def on_ok() -> None:
        name = name_entry.get().strip()
        if name:
            result["name"] = name
        dialog.destroy()

    def on_cancel() -> None:
        dialog.destroy()

    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)

    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)
    root.destroy()

    return result["name"]


def create_speaker_resolution_callback() -> Callable[..., str | None]:
    """Create a UI callback function for speaker resolution.

    Returns:
        Callback function that can be passed to enhance_text
    """

    def ui_callback(speaker_label: str, sample_utterances: list[str]) -> str | None:
        """UI callback for resolving speaker identities.

        Args:
            speaker_label: The speaker label to resolve
            sample_utterances: Sample utterances from this speaker

        Returns:
            Person name, or None if user cancelled
        """
        return prompt_speaker_mapping(speaker_label, sample_utterances)

    return ui_callback

"""Comprehensive unit tests for UI module."""

# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

from unittest.mock import MagicMock, patch

import pytest

from transcript_etl_pipeline.ui import (
    _is_debugger_active,  # pyright: ignore[reportPrivateUsage]
    _prompt_speaker_mapping_console,  # pyright: ignore[reportPrivateUsage]
    _prompt_speaker_mapping_gui,  # pyright: ignore[reportPrivateUsage]
    check_tkinter_available,
    create_speaker_resolution_callback,
    prompt_file_selection,
    prompt_format_selection,
    prompt_output_folder,
    prompt_output_name,
    prompt_source_selection,
    prompt_speaker_mapping,
    show_error,
    show_info,
)


class TestIsDebuggerActive:
    """Tests for debugger detection."""

    def test_returns_false_when_no_debugger(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return False when no debugger is active."""
        # Mock sys module to control gettrace and modules

        mock_sys = MagicMock()
        mock_sys.gettrace = lambda: None
        mock_sys.modules = {}

        with (
            patch("transcript_etl_pipeline.ui.sys", mock_sys),
            patch("transcript_etl_pipeline.ui.os.environ.get", return_value=None),
        ):
            assert _is_debugger_active() is False

    def test_returns_true_when_gettrace_active(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return True when sys.gettrace indicates active tracing."""
        monkeypatch.setattr("sys.gettrace", lambda: lambda *args: None, raising=False)  # type: ignore[reportUnknownLambdaType]
        monkeypatch.delenv("PYTHONBREAKPOINT", raising=False)

        assert _is_debugger_active() is True

    def test_returns_true_when_debugpy_loaded(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return True when debugpy module is loaded."""
        monkeypatch.setattr("sys.gettrace", lambda: None)
        mock_debugpy = MagicMock()
        monkeypatch.setitem(__import__("sys").modules, "debugpy", mock_debugpy)
        monkeypatch.delenv("PYTHONBREAKPOINT", raising=False)

        assert _is_debugger_active() is True

    def test_returns_true_when_pythonbreakpoint_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return True when PYTHONBREAKPOINT environment variable is set."""
        monkeypatch.setattr("sys.gettrace", lambda: None)
        monkeypatch.setitem(__import__("sys").modules, "debugpy", None)
        monkeypatch.setenv("PYTHONBREAKPOINT", "pdb.set_trace")

        assert _is_debugger_active() is True

    def test_handles_missing_gettrace(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should handle absence of sys.gettrace gracefully."""
        monkeypatch.delattr("sys.gettrace", raising=False)
        monkeypatch.delenv("PYTHONBREAKPOINT", raising=False)

        # Should not raise, should return False
        assert _is_debugger_active() is False


class TestCheckTkinterAvailable:
    """Tests for tkinter availability check."""

    def test_raises_when_tkinter_unavailable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should raise RuntimeError when tkinter is not available."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", False)

        with pytest.raises(RuntimeError, match="tkinter is not available"):
            check_tkinter_available()

    def test_succeeds_when_tkinter_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should not raise when tkinter is available."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        # Should not raise
        check_tkinter_available()


class TestShowError:
    """Tests for error dialog display."""

    def test_shows_error_dialog(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should display error dialog with correct title and message."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_messagebox = MagicMock()
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.messagebox", mock_messagebox)

        show_error("Error Title", "Error message text")

        mock_tk.Tk.assert_called_once()
        root = mock_tk.Tk.return_value
        root.withdraw.assert_called_once()
        mock_messagebox.showerror.assert_called_once_with("Error Title", "Error message text")
        root.destroy.assert_called_once()

    def test_raises_when_tkinter_unavailable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should raise RuntimeError when tkinter is not available."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", False)

        with pytest.raises(RuntimeError, match="tkinter is not available"):
            show_error("Title", "Message")

    def test_raises_when_tk_is_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should raise RuntimeError when tk module is None."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", None)

        with pytest.raises(RuntimeError, match="tkinter is not available"):
            show_error("Title", "Message")


class TestShowInfo:
    """Tests for info dialog display."""

    def test_shows_info_dialog(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should display info dialog with correct title and message."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_messagebox = MagicMock()
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.messagebox", mock_messagebox)

        show_info("Info Title", "Info message text")

        mock_tk.Tk.assert_called_once()
        root = mock_tk.Tk.return_value
        root.withdraw.assert_called_once()
        mock_messagebox.showinfo.assert_called_once_with("Info Title", "Info message text")
        root.destroy.assert_called_once()

    def test_raises_when_tkinter_unavailable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should raise RuntimeError when tkinter is not available."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", False)

        with pytest.raises(RuntimeError, match="tkinter is not available"):
            show_info("Title", "Message")


class TestPromptSourceSelection:
    """Tests for source selection prompt."""

    def test_returns_clipboard_when_yes_selected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return 'clipboard' when user selects Yes."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_messagebox = MagicMock()
        mock_messagebox.askquestion.return_value = "yes"
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.messagebox", mock_messagebox)

        result = prompt_source_selection()

        assert result == "clipboard"
        mock_messagebox.askquestion.assert_called_once()

    def test_returns_file_when_no_selected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return 'file' when user selects No."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_messagebox = MagicMock()
        mock_messagebox.askquestion.return_value = "no"
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.messagebox", mock_messagebox)

        result = prompt_source_selection()

        assert result == "file"

    def test_returns_none_when_cancelled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return None when user cancels dialog."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_messagebox = MagicMock()
        mock_messagebox.askquestion.return_value = "cancel"
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.messagebox", mock_messagebox)

        result = prompt_source_selection()

        assert result is None

    def test_raises_when_tkinter_unavailable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should raise RuntimeError when tkinter is not available."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", False)

        with pytest.raises(RuntimeError, match="tkinter is not available"):
            prompt_source_selection()


class TestPromptFileSelection:
    """Tests for file selection prompt."""

    def test_returns_selected_file_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return the selected file path."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_filedialog = MagicMock()
        mock_filedialog.askopenfilename.return_value = "/path/to/file.txt"
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.filedialog", mock_filedialog)

        result = prompt_file_selection()

        assert result == "/path/to/file.txt"
        mock_filedialog.askopenfilename.assert_called_once()

    def test_returns_none_when_cancelled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return None when user cancels file dialog."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_filedialog = MagicMock()
        mock_filedialog.askopenfilename.return_value = ""
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.filedialog", mock_filedialog)

        result = prompt_file_selection()

        assert result is None

    def test_configures_file_types(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should configure appropriate file type filters."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_filedialog = MagicMock()
        mock_filedialog.askopenfilename.return_value = ""
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.filedialog", mock_filedialog)

        prompt_file_selection()

        call_kwargs = mock_filedialog.askopenfilename.call_args[1]
        assert "filetypes" in call_kwargs
        filetypes = call_kwargs["filetypes"]
        assert any("*.txt" in str(ft) for ft in filetypes)
        assert any("*.md" in str(ft) for ft in filetypes)


class TestPromptFormatSelection:
    """Tests for format selection prompt."""

    def test_returns_selected_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return the format selected by user."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_toplevel = MagicMock()
        mock_tk.Toplevel.return_value = mock_toplevel
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)

        # Simulate user clicking "docx" button
        def wait_window_side_effect(dialog: object) -> None:
            # Find the button callbacks and trigger docx
            for call_item in mock_tk.Button.call_args_list:
                if call_item[1].get("text") == "DOCX (Microsoft Word)":
                    callback = call_item[1]["command"]
                    callback()
                    break

        mock_tk.Tk.return_value.wait_window.side_effect = wait_window_side_effect

        result = prompt_format_selection()

        assert result == "docx"

    def test_returns_none_when_dialog_closed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return None when dialog is closed without selection."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)

        result = prompt_format_selection()

        assert result is None


class TestPromptOutputName:
    """Tests for output name prompt."""

    def test_returns_entered_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return the filename entered by user."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_simpledialog = MagicMock()
        mock_simpledialog.askstring.return_value = "my_output.docx"
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.simpledialog", mock_simpledialog)

        result = prompt_output_name("default.docx")

        assert result == "my_output.docx"
        mock_simpledialog.askstring.assert_called_once()

    def test_returns_none_when_cancelled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return None when user cancels the dialog."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_simpledialog = MagicMock()
        mock_simpledialog.askstring.return_value = ""
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.simpledialog", mock_simpledialog)

        result = prompt_output_name("default.docx")

        assert result is None

    def test_uses_default_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should pass default name to dialog."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_simpledialog = MagicMock()
        mock_simpledialog.askstring.return_value = "output.docx"
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.simpledialog", mock_simpledialog)

        prompt_output_name("my_default.docx")

        call_kwargs = mock_simpledialog.askstring.call_args[1]
        assert call_kwargs["initialvalue"] == "my_default.docx"


class TestPromptOutputFolder:
    """Tests for output folder prompt."""

    def test_returns_selected_folder(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return the selected folder path."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_filedialog = MagicMock()
        mock_filedialog.askdirectory.return_value = "/path/to/folder"
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.filedialog", mock_filedialog)

        result = prompt_output_folder()

        assert result == "/path/to/folder"

    def test_returns_none_when_cancelled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return None when user cancels the dialog."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_filedialog = MagicMock()
        mock_filedialog.askdirectory.return_value = ""
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.filedialog", mock_filedialog)

        result = prompt_output_folder()

        assert result is None

    def test_uses_default_folder_when_exists(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should use default folder as initial directory when it exists."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_filedialog = MagicMock()
        mock_filedialog.askdirectory.return_value = "/some/path"
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.filedialog", mock_filedialog)

        with patch("transcript_etl_pipeline.ui.Path") as mock_path:
            mock_path.return_value.exists.return_value = True
            prompt_output_folder("/existing/folder")

        call_kwargs = mock_filedialog.askdirectory.call_args[1]
        assert call_kwargs["initialdir"] == "/existing/folder"

    def test_ignores_nonexistent_default_folder(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should not use default folder if it doesn't exist."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_filedialog = MagicMock()
        mock_filedialog.askdirectory.return_value = ""
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)
        monkeypatch.setattr("transcript_etl_pipeline.ui.filedialog", mock_filedialog)

        with patch("transcript_etl_pipeline.ui.Path") as mock_path:
            mock_path.return_value.exists.return_value = False
            prompt_output_folder("/nonexistent/folder")

        call_kwargs = mock_filedialog.askdirectory.call_args[1]
        assert call_kwargs["initialdir"] is None


class TestPromptSpeakerMapping:
    """Tests for speaker mapping prompt dispatcher."""

    def test_uses_console_when_debugger_active(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should use console prompt when debugger is active."""
        with (
            patch("transcript_etl_pipeline.ui._is_debugger_active", return_value=True),
            patch(
                "transcript_etl_pipeline.ui._prompt_speaker_mapping_console", return_value="Alice"
            ) as mock_console,
        ):
            result = prompt_speaker_mapping("Speaker A", ["Hello there"], ["Alice", "Bob"])

            assert result == "Alice"
            mock_console.assert_called_once_with("Speaker A", ["Hello there"], ["Alice", "Bob"])

    def test_uses_gui_when_no_debugger(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should use GUI prompt when no debugger is active."""
        with (
            patch("transcript_etl_pipeline.ui._is_debugger_active", return_value=False),
            patch(
                "transcript_etl_pipeline.ui._prompt_speaker_mapping_gui", return_value="Bob"
            ) as mock_gui,
        ):
            result = prompt_speaker_mapping("Speaker B", ["Hi everyone"], ["Alice", "Bob"])

            assert result == "Bob"
            mock_gui.assert_called_once_with("Speaker B", ["Hi everyone"], ["Alice", "Bob"])

    def test_falls_back_to_console_when_gui_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should fall back to console prompt when GUI raises exception."""
        with (
            patch("transcript_etl_pipeline.ui._is_debugger_active", return_value=False),
            patch(
                "transcript_etl_pipeline.ui._prompt_speaker_mapping_gui",
                side_effect=Exception("GUI failed"),
            ),
            patch(
                "transcript_etl_pipeline.ui._prompt_speaker_mapping_console", return_value="Charlie"
            ) as mock_console,
        ):
            result = prompt_speaker_mapping("Speaker C", ["Good morning"], ["Charlie"])

            assert result == "Charlie"
            mock_console.assert_called_once()


class TestPromptSpeakerMappingConsole:
    """Tests for console-based speaker mapping."""

    def test_returns_selected_candidate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return the selected candidate name."""
        inputs = ["1"]  # Select first candidate
        monkeypatch.setattr("builtins.input", lambda _: inputs.pop(0))

        result = _prompt_speaker_mapping_console(
            "Speaker A", ["Hello everyone", "How are you?"], ["Alice", "Bob", "Charlie"]
        )

        assert result == "Alice"

    def test_returns_other_name_when_other_selected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should prompt for manual name entry when 'Other' is selected."""
        inputs = ["4", "David"]  # Select "Other" (option 4), then enter "David"
        monkeypatch.setattr("builtins.input", lambda _: inputs.pop(0))

        result = _prompt_speaker_mapping_console(
            "Speaker A", ["Hello"], ["Alice", "Bob", "Charlie"]
        )

        assert result == "David"

    def test_returns_none_when_user_skips(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return None when user presses Enter to skip."""
        inputs = [""]  # Press Enter
        monkeypatch.setattr("builtins.input", lambda _: inputs.pop(0))

        result = _prompt_speaker_mapping_console("Speaker A", ["Hello"], ["Alice"])

        assert result is None

    def test_validates_numeric_input(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should validate numeric input and re-prompt on invalid."""
        inputs = ["abc", "5", "1"]  # Invalid, out of range, then valid
        monkeypatch.setattr("builtins.input", lambda _: inputs.pop(0))

        result = _prompt_speaker_mapping_console("Speaker A", ["Hello"], ["Alice"])

        assert result == "Alice"

    def test_validates_choice_range(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should validate choice is within valid range."""
        inputs = ["0", "5", "2"]  # Too low, too high, then valid
        monkeypatch.setattr("builtins.input", lambda _: inputs.pop(0))

        result = _prompt_speaker_mapping_console("Speaker A", ["Hello"], ["Alice", "Bob"])

        assert result == "Bob"

    def test_handles_empty_name_for_other(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should re-prompt when user selects Other but enters empty name."""
        inputs = ["2", "", "2", "Carol"]  # Select Other, empty name, retry
        monkeypatch.setattr("builtins.input", lambda _: inputs.pop(0))

        result = _prompt_speaker_mapping_console("Speaker A", ["Hello"], ["Alice"])

        assert result == "Carol"

    def test_truncates_long_samples(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Should truncate samples longer than 150 characters."""
        inputs = [""]  # Skip
        monkeypatch.setattr("builtins.input", lambda _: inputs.pop(0))

        long_sample = "A" * 200
        _prompt_speaker_mapping_console("Speaker A", [long_sample], ["Alice"])

        captured = capsys.readouterr()
        assert "..." in captured.out
        assert "A" * 200 not in captured.out

    def test_displays_multiple_candidates(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Should display all candidate options."""
        inputs = [""]
        monkeypatch.setattr("builtins.input", lambda _: inputs.pop(0))

        _prompt_speaker_mapping_console("Speaker A", ["Hello"], ["Alice", "Bob", "Charlie"])

        captured = capsys.readouterr()
        assert "1. Alice" in captured.out
        assert "2. Bob" in captured.out
        assert "3. Charlie" in captured.out
        assert "4. Other" in captured.out


class TestPromptSpeakerMappingGui:
    """Tests for GUI-based speaker mapping."""

    def test_returns_selected_candidate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return the name of selected candidate."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_toplevel = MagicMock()
        mock_stringvar = MagicMock()
        mock_stringvar.get.return_value = "Alice"

        mock_tk.Toplevel.return_value = mock_toplevel
        mock_tk.StringVar.return_value = mock_stringvar
        mock_tk.WORD = "word"
        mock_tk.END = "end"
        mock_tk.DISABLED = "disabled"
        mock_tk.LEFT = "left"

        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)

        # Simulate OK button click
        def wait_window_side_effect(dialog: object) -> None:
            for call_item in mock_tk.Button.call_args_list:
                if call_item[1].get("text") == "OK":
                    callback = call_item[1]["command"]
                    callback()
                    break

        mock_tk.Tk.return_value.wait_window.side_effect = wait_window_side_effect

        result = _prompt_speaker_mapping_gui("Speaker A", ["Hello"], ["Alice", "Bob"])

        assert result == "Alice"

    def test_returns_manual_entry_when_other_selected(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should return manually entered name when Other is selected."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_toplevel = MagicMock()
        mock_stringvar = MagicMock()
        mock_stringvar.get.return_value = "__OTHER__"
        mock_entry = MagicMock()
        mock_entry.get.return_value = "Charlie"

        mock_tk.Toplevel.return_value = mock_toplevel
        mock_tk.StringVar.return_value = mock_stringvar
        mock_tk.Entry.return_value = mock_entry
        mock_tk.WORD = "word"
        mock_tk.END = "end"
        mock_tk.DISABLED = "disabled"
        mock_tk.LEFT = "left"

        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)

        def wait_window_side_effect(dialog: object) -> None:
            for call_item in mock_tk.Button.call_args_list:
                if call_item[1].get("text") == "OK":
                    callback = call_item[1]["command"]
                    callback()
                    break

        mock_tk.Tk.return_value.wait_window.side_effect = wait_window_side_effect

        result = _prompt_speaker_mapping_gui("Speaker A", ["Hello"], ["Alice"])

        assert result == "Charlie"

    def test_returns_none_when_cancelled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return None when Skip button is clicked."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_tk.WORD = "word"
        mock_tk.END = "end"
        mock_tk.DISABLED = "disabled"
        mock_tk.LEFT = "left"
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)

        def wait_window_side_effect(dialog: object) -> None:
            for call_item in mock_tk.Button.call_args_list:
                if call_item[1].get("text") == "Skip":
                    callback = call_item[1]["command"]
                    callback()
                    break

        mock_tk.Tk.return_value.wait_window.side_effect = wait_window_side_effect

        result = _prompt_speaker_mapping_gui("Speaker A", ["Hello"], ["Alice"])

        assert result is None

    def test_displays_samples_in_text_box(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should display sample utterances in text box."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_text = MagicMock()
        mock_tk.Text.return_value = mock_text
        mock_tk.WORD = "word"
        mock_tk.END = "end"
        mock_tk.DISABLED = "disabled"
        mock_tk.LEFT = "left"
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)

        mock_tk.Tk.return_value.wait_window.side_effect = lambda _: None

        _prompt_speaker_mapping_gui(
            "Speaker A", ["First sample", "Second sample", "Third sample"], ["Alice"]
        )

        # Check that text was inserted
        assert mock_text.insert.call_count >= 3

    def test_limits_samples_to_three(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should display at most three sample utterances."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_text = MagicMock()
        mock_tk.Text.return_value = mock_text
        mock_tk.WORD = "word"
        mock_tk.END = "end"
        mock_tk.DISABLED = "disabled"
        mock_tk.LEFT = "left"
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)

        mock_tk.Tk.return_value.wait_window.side_effect = lambda _: None

        samples = [f"Sample {i}" for i in range(10)]
        _prompt_speaker_mapping_gui("Speaker A", samples, ["Alice"])

        # Should only insert 3 samples (each with newlines = 3 calls with actual text)
        text_inserts = [
            call_item
            for call_item in mock_text.insert.call_args_list
            if "Sample" in str(call_item[0][1])
        ]
        assert len(text_inserts) == 3

    def test_creates_radio_buttons_for_candidates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should create radio buttons for each candidate."""
        monkeypatch.setattr("transcript_etl_pipeline.ui._tkinter_available", True)

        mock_tk = MagicMock()
        mock_tk.WORD = "word"
        mock_tk.END = "end"
        mock_tk.DISABLED = "disabled"
        mock_tk.LEFT = "left"
        monkeypatch.setattr("transcript_etl_pipeline.ui.tk", mock_tk)

        mock_tk.Tk.return_value.wait_window.side_effect = lambda _: None

        _prompt_speaker_mapping_gui("Speaker A", ["Hello"], ["Alice", "Bob", "Charlie"])

        # Check that radiobuttons were created for candidates
        radiobutton_calls = [
            call_item for call_item in mock_tk.Radiobutton.call_args_list if "text" in call_item[1]
        ]
        assert len(radiobutton_calls) >= 3  # At least 3 candidates + Other option


class TestCreateSpeakerResolutionCallback:
    """Tests for speaker resolution callback creation."""

    def test_returns_callable(self) -> None:
        """Should return a callable function."""
        callback = create_speaker_resolution_callback()

        assert callable(callback)

    def test_callback_delegates_to_prompt_speaker_mapping(self) -> None:
        """Should create a callback that delegates to prompt_speaker_mapping."""
        with patch(
            "transcript_etl_pipeline.ui.prompt_speaker_mapping", return_value="Alice"
        ) as mock_prompt:
            callback = create_speaker_resolution_callback()
            result = callback("Speaker A", ["Hello"], ["Alice", "Bob"])

            assert result == "Alice"
            mock_prompt.assert_called_once_with("Speaker A", ["Hello"], ["Alice", "Bob"])

    def test_callback_returns_none_when_cancelled(self) -> None:
        """Should return None when user cancels the mapping."""
        with patch("transcript_etl_pipeline.ui.prompt_speaker_mapping", return_value=None):
            callback = create_speaker_resolution_callback()
            result = callback("Speaker A", ["Hello"], ["Alice"])

            assert result is None

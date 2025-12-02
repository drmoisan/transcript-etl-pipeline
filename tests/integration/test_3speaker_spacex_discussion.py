"""Integration test for 3-speaker SpaceX discussion transcript.

This test validates the speakerless detection on a complex real-world scenario:
- Three speakers discussing a SpaceX launch
- Natural conversational flow with references to named individuals (Devin, Chris)
- No explicit speaker labels in input
- Expected output has generic Speaker A/B/C labels

This is a challenging test case because:
1. Names are mentioned in dialogue ("Devin", "Chris") but should not be confused with speaker labels
2. The conversation has natural turn-taking with varied sentence lengths
3. Multiple speakers need to be distinguished without explicit identity markers
"""

from pathlib import Path
from typing import TypedDict

import pytest

from transcript_etl_pipeline.transform.speakerless import assign_speaker_labels


class MismatchDict(TypedDict):
    """Type definition for mismatch dictionary."""

    line_num: int
    expected_speaker: str
    actual_speaker: str
    expected_content: str
    actual_content: str
    speaker_match: bool
    content_match: bool


# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "sample_transcripts"


class TestThreeSpeakerSpaceXDiscussion:
    """Integration test for 3-speaker SpaceX discussion without speaker labels."""

    def test_fixture_files_exist(self) -> None:
        """Verify both input and expected output fixtures exist."""
        input_path = FIXTURES_DIR / "ts_3speakers_no_speakers.txt"
        expected_path = FIXTURES_DIR / "ts_3speakers_fully_generic_speakers.txt"

        assert input_path.exists(), f"Input fixture not found: {input_path}"
        assert expected_path.exists(), f"Expected output fixture not found: {expected_path}"

    @pytest.mark.stress_test
    @pytest.mark.xfail(
        reason="Complex 3-speaker detection requires algorithmic improvements. "
        "See docs/3speaker-spacex-test-analysis.md for detailed failure analysis.",
        strict=False,
    )
    def test_three_speaker_detection_and_assignment(self) -> None:
        """Test full pipeline: detect 3 speakers and assign labels matching expected output.

        This test compares actual output against the expected generic Speaker A/B/C format.
        It documents any discrepancies between algorithm output and expected results.
        """
        # Load input (no speaker labels)
        input_path = FIXTURES_DIR / "ts_3speakers_no_speakers.txt"
        input_text = input_path.read_text(encoding="utf-8")

        # Load expected output (with generic Speaker A/B/C labels)
        expected_path = FIXTURES_DIR / "ts_3speakers_fully_generic_speakers.txt"
        expected_text = expected_path.read_text(encoding="utf-8")

        # Extract just the transcript section from expected output
        # (Skip metadata header: "Meeting Title:", "Date:", "Transcript:")
        expected_lines = expected_text.split("\n")
        transcript_start = None
        for i, line in enumerate(expected_lines):
            if line.strip() == "Transcript:":
                transcript_start = i + 1
                break

        assert (
            transcript_start is not None
        ), "Could not find 'Transcript:' marker in expected output"

        # Get expected transcript lines (skip empty lines at start)
        expected_transcript_lines: list[str] = []
        for line in expected_lines[transcript_start:]:
            if line.strip():  # Skip empty lines
                expected_transcript_lines.append(line.strip())

        # Similarly, extract input transcript section
        input_lines = input_text.split("\n")
        input_transcript_start = None
        for i, line in enumerate(input_lines):
            if line.strip() == "Transcript:":
                input_transcript_start = i + 1
                break

        assert input_transcript_start is not None, "Could not find 'Transcript:' marker in input"

        # Get input transcript text (everything after "Transcript:" header)
        input_transcript_text = "\n".join(input_lines[input_transcript_start:]).strip()

        # Run the speakerless detection with 3 speakers
        actual_output = assign_speaker_labels(input_transcript_text, num_speakers=3)

        # Split actual output into lines
        actual_lines = [line.strip() for line in actual_output.split("\r\n") if line.strip()]

        # Verify we got output
        assert len(actual_lines) > 0, "No output generated from speaker detection"

        # Document the comparison
        print("\n" + "=" * 80)
        print("THREE-SPEAKER SPACEX DISCUSSION: Actual vs Expected")
        print("=" * 80)
        print(f"\nExpected lines: {len(expected_transcript_lines)}")
        print(f"Actual lines: {len(actual_lines)}")
        print("\n" + "-" * 80)

        # Compare line by line and document discrepancies
        max_lines = max(len(expected_transcript_lines), len(actual_lines))
        mismatches: list[MismatchDict] = []

        for i in range(max_lines):
            expected_line = (
                expected_transcript_lines[i] if i < len(expected_transcript_lines) else "[MISSING]"
            )
            actual_line = actual_lines[i] if i < len(actual_lines) else "[MISSING]"

            # Extract speaker label and content
            if expected_line != "[MISSING]" and ":" in expected_line:
                expected_speaker = expected_line.split(":")[0].strip()
                expected_content = expected_line.split(":", 1)[1].strip()
            else:
                expected_speaker = "[MISSING]"
                expected_content = expected_line

            if actual_line != "[MISSING]" and ":" in actual_line:
                actual_speaker = actual_line.split(":")[0].strip()
                actual_content = actual_line.split(":", 1)[1].strip()
            else:
                actual_speaker = "[MISSING]"
                actual_content = actual_line

            # Compare
            speaker_match = expected_speaker == actual_speaker
            content_match = expected_content == actual_content

            if not speaker_match or not content_match:
                mismatches.append(
                    {
                        "line_num": i,
                        "expected_speaker": expected_speaker,
                        "actual_speaker": actual_speaker,
                        "expected_content": expected_content[:100],
                        "actual_content": actual_content[:100],
                        "speaker_match": speaker_match,
                        "content_match": content_match,
                    }
                )

            # Print comparison
            match_indicator = "✓" if (speaker_match and content_match) else "✗"
            print(f"Line {i:2d} {match_indicator}")
            print(f"  Expected: {expected_speaker:10s} | {expected_content[:70]}")
            print(f"  Actual:   {actual_speaker:10s} | {actual_content[:70]}")
            if not speaker_match:
                print("  >>> SPEAKER MISMATCH <<<")
            if not content_match:
                print("  >>> CONTENT MISMATCH <<<")
            print()

        # Summary
        print("=" * 80)
        print(f"SUMMARY: {len(mismatches)} mismatches out of {max_lines} lines")
        print("=" * 80)

        if mismatches:
            print("\nDETAILED MISMATCH ANALYSIS:")
            print("-" * 80)

            for mismatch in mismatches:
                print(f"\nLine {mismatch['line_num']}:")
                print(f"  Expected Speaker: {mismatch['expected_speaker']}")
                print(f"  Actual Speaker:   {mismatch['actual_speaker']}")
                print(f"  Content Match:    {mismatch['content_match']}")
                print(f"  Expected Content: {mismatch['expected_content']}")
                print(f"  Actual Content:   {mismatch['actual_content']}")

        print("\n" + "=" * 80)
        print("FAILURE ANALYSIS")
        print("=" * 80)

        # Analyze the nature of failures
        self._analyze_failures(mismatches, expected_transcript_lines, actual_lines)

        # The test fails if there are mismatches (but still runs to completion for documentation)
        assert len(mismatches) == 0, (
            f"Found {len(mismatches)} mismatches between expected and actual output. "
            f"See detailed analysis above."
        )

    def _analyze_failures(
        self,
        mismatches: list[MismatchDict],
        expected_lines: list[str],
        actual_lines: list[str],
    ) -> None:
        """Analyze the nature of failures and document logic issues vs text ambiguities.

        For each mismatch, determine:
        1. Is the correct answer knowable from context? (Logic weakness)
        2. Is the text inherently ambiguous? (Text limitation)
        3. What improvement would resolve the issue?
        """
        if not mismatches:
            print("\n✓ No failures to analyze - perfect match!")
            return

        print("\nAnalyzing failure patterns...\n")

        # Categorize failures
        speaker_assignment_errors: list[MismatchDict] = []
        content_grouping_errors: list[MismatchDict] = []

        for mismatch in mismatches:
            if not mismatch["speaker_match"]:
                speaker_assignment_errors.append(mismatch)
            if not mismatch["content_match"]:
                content_grouping_errors.append(mismatch)

        print(f"Speaker Assignment Errors: {len(speaker_assignment_errors)}")
        print(f"Content Grouping Errors: {len(content_grouping_errors)}")
        print()

        # Analyze speaker assignment errors
        if speaker_assignment_errors:
            print("SPEAKER ASSIGNMENT ANALYSIS:")
            print("-" * 80)
            print("\nThese are cases where the algorithm assigned a different speaker")
            print("than the expected output. Each should be evaluated for:")
            print("  1. Is the correct speaker knowable from context?")
            print("  2. What contextual cues should the algorithm use?")
            print("  3. Is this a limitation of the text or the algorithm?")
            print()

            for error in speaker_assignment_errors[:5]:  # Show first 5
                print(f"Line {error['line_num']}:")
                print(f"  Expected: {error['expected_speaker']}")
                print(f"  Actual:   {error['actual_speaker']}")
                print(f"  Content:  {error['expected_content']}")
                print()

                # Attempt to identify the issue type
                content_lower = error["expected_content"].lower()

                if any(name in content_lower for name in ["devin", "chris"]):
                    print("  ⚠️  Contains name reference - may indicate addressee detection needed")
                elif content_lower.startswith(("hey,", "hi,", "hello,")):
                    print("  ⚠️  Greeting pattern - likely turn-taking marker")
                elif "?" in error["expected_content"]:
                    print("  ⚠️  Contains question - response pattern detection may help")
                elif content_lower.startswith(("yeah,", "yes,", "right?", "true")):
                    print("  ⚠️  Acknowledgment - may need better acknowledgment detection")
                else:
                    print("  ❓ No obvious pattern - may need deeper discourse analysis")
                print()

        # Analyze content grouping errors
        if content_grouping_errors:
            print("\nCONTENT GROUPING ANALYSIS:")
            print("-" * 80)
            print("\nThese are cases where sentences were grouped differently than expected.")
            print("This could indicate:")
            print("  1. Speaker change detection is too aggressive (over-splitting)")
            print("  2. Speaker change detection is too conservative (under-splitting)")
            print("  3. Sentence tokenization differs from expected")
            print()

        # Overall assessment
        print("\nOVERALL ASSESSMENT:")
        print("-" * 80)

        if len(mismatches) < 5:
            severity = "Minor"
            recommendation = "Small adjustments to heuristics may resolve most issues"
        elif len(mismatches) < 15:
            severity = "Moderate"
            recommendation = "Significant heuristic improvements needed for this conversation style"
        else:
            severity = "Major"
            recommendation = "May require new detection strategies or manual intervention"

        print(f"Severity: {severity}")
        print(f"Recommendation: {recommendation}")
        print()

        # Specific improvements needed
        print("SUGGESTED IMPROVEMENTS:")
        print("-" * 80)

        improvements: set[str] = set()

        for error in speaker_assignment_errors:
            content_lower = error["expected_content"].lower()

            if any(name in content_lower for name in ["devin", "chris"]):
                improvements.add(
                    "1. Implement addressee detection: when someone says 'Hey Chris', "
                    "the speaker is likely NOT Chris"
                )

            if content_lower.startswith(("hey,", "hi,")):
                improvements.add(
                    "2. Enhance greeting detection: greetings at start of sentences "
                    "are strong turn-taking markers"
                )

            if any(ack in content_lower for ack in ["yeah,", "right?", "true,", "exactly"]):
                improvements.add(
                    "3. Improve acknowledgment patterns: include more conversational "
                    "acknowledgments like 'exactly', 'true', etc."
                )

        if not improvements:
            improvements.add(
                "1. This conversation style may require identity-aware detection or "
                "user intervention to resolve speaker ambiguities"
            )

        for improvement in sorted(improvements):
            print(f"  {improvement}")

        print()

"""Quick test to verify the exact output of the three-speaker scenario."""

from transcript_etl_pipeline.transform.speakerless import assign_speaker_labels

text = (
    "Welcome everyone to the meeting. Thanks for having us. Yes, thank you so much. "
    "No problem. Let's start with introductions. You both know me. I'm Peter Parker, "
    "and I thought it would be great for you two to meet. Who wants to go first? "
    "Sure, I'll go first. Thanks Frank, go ahead. Ok. My name is Frank Oz, and I like "
    "puppets. Thanks Frank. Fred? Oh yes, I'm Fred Flintstone. Great. Thank you both"
)

expected_output = (
    "Speaker A: Welcome everyone to the meeting.\n"
    "Speaker B: Thanks for having us.\n"
    "Speaker C: Yes, thank you so much.\n"
    "Speaker A: No problem. Let's start with introductions. "
    "You both know me. I'm Peter Parker, and I thought it would be great for you two to meet. "
    "Who wants to go first?\n"
    "Speaker B: Sure, I'll go first.\n"
    "Speaker A: Thanks Frank, go ahead.\n"
    "Speaker B: Ok. My name is Frank Oz, and I like puppets.\n"
    "Speaker A: Thanks Frank. Fred?\n"
    "Speaker C: Oh yes, I'm Fred Flintstone.\n"
    "Speaker A: Great. Thank you both"
)

result = assign_speaker_labels(text, num_speakers=3)

print("ACTUAL OUTPUT:")
print(result)
print("\n" + "=" * 80 + "\n")
print("EXPECTED OUTPUT:")
print(expected_output)
print("\n" + "=" * 80 + "\n")

# Compare line by line
result_lines = [line for line in result.split("\r\n") if line.strip()]
expected_lines = [line for line in expected_output.split("\n") if line.strip()]

print(f"Result lines: {len(result_lines)}")
print(f"Expected lines: {len(expected_lines)}")
print()

if len(result_lines) != len(expected_lines):
    print("WARNING: Line count mismatch!")
    print()

matches = 0
mismatches: list[tuple[int, str, str]] = []
for i in range(max(len(result_lines), len(expected_lines))):
    if i < len(result_lines) and i < len(expected_lines):
        r = result_lines[i]
        e = expected_lines[i]
        if r == e:
            matches += 1
            print(f"Line {i}: ✓ MATCH")
        else:
            print(f"Line {i}: ✗ MISMATCH")
            print(f"  Expected: {e}")
            print(f"  Got:      {r}")
            mismatches.append((i, e, r))
    elif i < len(result_lines):
        print(f"Line {i}: ✗ EXTRA in result: {result_lines[i]}")
    else:
        print(f"Line {i}: ✗ MISSING in result: {expected_lines[i]}")

print(f"\nSummary: {matches}/{len(expected_lines)} lines match")

if matches == len(expected_lines) and len(result_lines) == len(expected_lines):
    print("\n✓✓✓ SUCCESS: Output matches expected! ✓✓✓")
else:
    print("\n✗✗✗ FAILURE: Output does not match expected ✗✗✗")

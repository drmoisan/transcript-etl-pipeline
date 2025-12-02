"""Debug script to trace through the speaker assignment logic."""

from transcript_etl_pipeline.transform.identity_constraints import extract_identity_constraints
from transcript_etl_pipeline.transform.speaker_helpers import group_sentences_by_similarity
from transcript_etl_pipeline.transform.speakerless import (
    assign_speaker_labels,
    detect_speaker_changes,
    tokenize_into_sentences,
)

text = (
    "Welcome everyone to the meeting. Thanks for having us. Yes, thank you so much. "
    "No problem. Let's start with introductions. You both know me. I'm Peter Parker, "
    "and I thought it would be great for you two to meet. Who wants to go first? "
    "Sure, I'll go first. Thanks Frank, go ahead. Ok. My name is Frank Oz, and I like "
    "puppets. Thanks Frank. Fred? Oh yes, I'm Fred Flintstone. Great. Thank you both"
)

print("=" * 80)
print("STEP 1: Tokenize sentences")
print("=" * 80)
sentences = tokenize_into_sentences(text)
for i, sent in enumerate(sentences):
    print(f"  {i}: {sent}")

print("\n" + "=" * 80)
print("STEP 2: Detect speaker changes")
print("=" * 80)
change_points = detect_speaker_changes(text)
print(f"Change points: {change_points}")

print("\n" + "=" * 80)
print("STEP 3: Extract identity constraints")
print("=" * 80)
constraints = extract_identity_constraints(sentences)
for c in constraints:
    print(f"  {c}")

print("\n" + "=" * 80)
print("STEP 4: Group by similarity (with constraints)")
print("=" * 80)
assignments = group_sentences_by_similarity(sentences, change_points, 3, constraints)
print(f"Assignments: {assignments}")

print("\n" + "=" * 80)
print("STEP 5: Map to speaker labels")
print("=" * 80)
speaker_map = {0: "A", 1: "B", 2: "C"}
for i, (sent, speaker_idx) in enumerate(zip(sentences, assignments, strict=False)):
    speaker_label = speaker_map.get(speaker_idx, "?")
    print(f"  {i}: Speaker {speaker_label}: {sent}")

print("\n" + "=" * 80)
print("STEP 6: Full pipeline with post-processing")
print("=" * 80)
result = assign_speaker_labels(text, num_speakers=3)
result_lines = [line for line in result.split("\r\n") if line.strip()]
for i, line in enumerate(result_lines):
    print(f"  {i}: {line}")

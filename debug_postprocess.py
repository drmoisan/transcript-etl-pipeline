"""Debug script with detailed post-processing trace."""

from transcript_etl_pipeline.transform.identity_constraints import extract_identity_constraints
from transcript_etl_pipeline.transform.speaker_helpers import (
    group_sentences_by_similarity,
    resolve_addresses_other_violations,
)
from transcript_etl_pipeline.transform.speakerless import (
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

sentences = tokenize_into_sentences(text)
change_points = detect_speaker_changes(text)
constraints = extract_identity_constraints(sentences)

print("BEFORE POST-PROCESSING:")
print("=" * 80)
assignments_before = group_sentences_by_similarity(sentences, change_points, 3, constraints)
for i, (sent, spk) in enumerate(zip(sentences, assignments_before, strict=False)):
    spk_label = chr(ord("A") + spk)
    marker = ""
    for c in constraints:
        if c.sentence_idx == i:
            marker = f" [{c.constraint_type}: {c.name}]"
            break
    print(f"  {i:2d}: Speaker {spk_label}: {sent}{marker}")

print("\n" + "=" * 80)
print("AFTER POST-PROCESSING:")
print("=" * 80)
assignments_after = resolve_addresses_other_violations(
    sentences, assignments_before, constraints, 3
)

changes = []
for i, (sent, spk_before, spk_after) in enumerate(
    zip(sentences, assignments_before, assignments_after, strict=False)
):
    spk_label_before = chr(ord("A") + spk_before)
    spk_label_after = chr(ord("A") + spk_after)
    marker = ""
    for c in constraints:
        if c.sentence_idx == i:
            marker = f" [{c.constraint_type}: {c.name}]"
            break

    if spk_before != spk_after:
        print(
            f"  {i:2d}: Speaker {spk_label_before} -> {spk_label_after}: {sent}{marker} **CHANGED**"
        )
        changes.append(i)
    else:
        print(f"  {i:2d}: Speaker {spk_label_after}: {sent}{marker}")

print("\n" + "=" * 80)
print(f"SUMMARY: {len(changes)} sentences reassigned")
if changes:
    print(f"Changed sentences: {changes}")

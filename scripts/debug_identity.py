"""Debug script to examine identity constraint extraction."""

from transcript_etl_pipeline.transform.identity_constraints import extract_identity_constraints
from transcript_etl_pipeline.transform.speakerless import tokenize_into_sentences

text = (
    "Welcome everyone to the meeting. Thanks for having us. Yes, thank you so much. "
    "No problem. Let's start with introductions. You both know me. I'm Peter Parker, "
    "and I thought it would be great for you two to meet. Who wants to go first? "
    "Sure, I'll go first. Thanks Frank, go ahead. Ok. My name is Frank Oz, and I like "
    "puppets. Thanks Frank. Fred? Oh yes, I'm Fred Flintstone. Great. Thank you both"
)

sentences = tokenize_into_sentences(text)
constraints = extract_identity_constraints(sentences)

print("SENTENCES:")
for i, sent in enumerate(sentences):
    print(f"  {i}: {sent}")

print("\n" + "=" * 80 + "\n")
print("IDENTITY CONSTRAINTS:")
for c in constraints:
    print(f"  {c}")
    print(f"    Sentence: {sentences[c.sentence_idx]}")

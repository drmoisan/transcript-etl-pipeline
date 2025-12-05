"""Reusable multi-speaker test fixtures for 3+ speaker transcript scenarios.

This module provides standardized test fixtures for multi-speaker transcripts,
designed to be imported and used by various test modules. These fixtures are
particularly useful for:

1. Testing speaker detection and assignment algorithms
2. Regression testing for grouping behavior
3. Integration testing with complex multi-party dialogues

Fixture Categories:
- SpaceX Discussion: 3-speaker technical conversation with named participants
- Generic Meeting: 3-speaker business meeting with formal turn-taking
- Panel Discussion: 4-speaker panel with diverse speaking styles

Each fixture includes:
- Raw input text (speakerless)
- Expected output with speaker labels
- Metadata about the fixture (speaker count, characteristics)

Usage Example:
    from tests.fixtures.multi_speaker import (
        SPACEX_DISCUSSION,
        GENERIC_MEETING_3SPEAKER,
    )

    def test_three_speaker_detection() -> None:
        result = assign_speaker_labels(SPACEX_DISCUSSION.input_text, num_speakers=3)
        # Verify result against expected patterns
"""

from dataclasses import dataclass
from pathlib import Path

# Path to sample transcripts directory
SAMPLE_TRANSCRIPTS_DIR = Path(__file__).parent / "sample_transcripts"


@dataclass(frozen=True)
class ExpectedSpeakerLine:
    """Represents an expected line of dialogue with speaker assignment.

    Attributes:
        speaker: Expected speaker label (e.g., "Speaker A", "Speaker B")
        content: The dialogue content for this line (may be partial match)
        line_index: Zero-based index of the line in expected output
    """

    speaker: str
    content: str
    line_index: int


@dataclass(frozen=True)
class MultiSpeakerFixture:
    """A complete multi-speaker test fixture.

    Attributes:
        name: Short name for the fixture (e.g., "spacex_discussion")
        description: Human-readable description of the scenario
        num_speakers: Number of distinct speakers in the transcript
        input_text: Raw speakerless transcript text
        expected_lines: List of expected speaker/content pairs
        characteristics: List of notable characteristics for testing
    """

    name: str
    description: str
    num_speakers: int
    input_text: str
    expected_lines: tuple[ExpectedSpeakerLine, ...]
    characteristics: tuple[str, ...]


def load_fixture_file(filename: str) -> str:
    """Load a fixture file from the sample_transcripts directory.

    Args:
        filename: Name of the file to load

    Returns:
        The file contents as a string

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    path = SAMPLE_TRANSCRIPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Fixture file not found: {path}")
    return path.read_text(encoding="utf-8")


# =============================================================================
# SpaceX Discussion Fixture (3 speakers)
# =============================================================================

# Load the SpaceX fixture files
_SPACEX_INPUT_TEXT = """Hey, Devin, Chris, did either of you catch the SpaceX launch this morning? I had the stream running while I was getting coffee, and I swear my heart rate went up during the countdown. Yeah, I watched it! The liftoff looked insanely smooth. I'm always amazed at how little lateral wobble there is now. Ten years ago, launches looked way rougher. I missed it live, but I watched the replay on my lunch break. The plume expansion once they cleared the thick atmosphere was gorgeous. It always blows my mind how the exhaust just blooms out like a flower. Right? And the booster landing—oh man. They stuck it again. Chris, do you remember watching together in 2015 when they first launched? It was headline news just because they attempted it. Now it's like, "Yep, another Tuesday." Yeah, I remember it. What got me this time was how fast they acquired the drone-ship telemetry. There was basically no delay before the landing confirmation. Usually we get that awkward 20 seconds of black screen while you just hope it didn't explode. That's because they upgraded the ground relay system last quarter. I think they're using the space-based relay partners more heavily now. It's wild; even the "boring" engineering updates make massive differences. Oh, interesting, Devin. I didn't know that. Did either of you notice they mentioned a new upper-stage engine config? Something about throttle precision for deep-space missions? Yeah, they said the redesigned injector plate gives them finer control at very low thrust levels. That's basically essential if they want to do long-duration burns for the Mars cargo missions. It also affects rendezvous accuracy for the lunar variant, I think. I read a thread on Reddit where someone explained that gentle burns reduce propellant slosh. Space is complicated. Speaking of Mars, did you hear the host kind of hinting that the next launch window might involve a prototype cargo stack? He was cagey, but you could tell he wanted to spill something. I caught that too! He said "the next mission profile is… interesting." That usually means they're flying something we haven't seen before. Maybe a payload simulator for the Mars transfer container? Or it could be a structural test for the long-duration tank. They need that data before they commit to the real cargo loads. I wouldn't read too much into the commentator's smile — those folks love to tease. Fair, but honestly everything about this program feels like it's accelerating. Even the rollout looked smoother. You can always tell how confident they are by how slowly the camera operators pan across the rocket. Ha! True. Also, I noticed the entire pre-launch checklist segment was shorter. That usually means fewer issues during fueling. When they're worried, they talk *a lot*. I'm just relieved the weather cooperated. There was a crosswind warning earlier in the week. You could see the clouds, but the upper-level winds were apparently perfect. So, overall: where does this launch fit in the bigger roadmap? Incremental step? Major milestone? I'd call it a medium milestone. Not the big flashy test flights, but an essential one. Without these steady data-gathering missions, the dramatic breakthroughs don't happen. Exactly. Space exploration is like stacking bricks. Today was a brick. A really well-placed one. And now I'm just waiting for the next one — hopefully something with new hardware or a crazy payload."""  # noqa: E501

# Expected speaker assignments for SpaceX (Speaker A/B/C rotating pattern)
# Based on the resolved version where Maya=A, Chris=B, Devin=C pattern
_SPACEX_EXPECTED_LINES = (
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Hey, Devin, Chris, did either of you catch the SpaceX launch",
        line_index=0,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker B",
        content="Yeah, I watched it! The liftoff looked insanely smooth",
        line_index=1,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker C",
        content="I missed it live, but I watched the replay on my lunch break",
        line_index=2,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Right? And the booster landing—oh man",
        line_index=3,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker B",
        content="Yeah, I remember it. What got me this time",
        line_index=4,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker C",
        content="That's because they upgraded the ground relay system",
        line_index=5,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Oh, interesting, Devin. I didn't know that",
        line_index=6,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker B",
        content="Yeah, they said the redesigned injector plate",
        line_index=7,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker C",
        content="It also affects rendezvous accuracy",
        line_index=8,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Speaking of Mars, did you hear the host",
        line_index=9,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker B",
        content='I caught that too! He said "the next mission profile',
        line_index=10,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker C",
        content="Or it could be a structural test for the long-duration tank",
        line_index=11,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Fair, but honestly everything about this program",
        line_index=12,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker B",
        content="Ha! True. Also, I noticed the entire pre-launch checklist",
        line_index=13,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker C",
        content="I'm just relieved the weather cooperated",
        line_index=14,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="So, overall: where does this launch fit in the bigger roadmap",
        line_index=15,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker B",
        content="I'd call it a medium milestone",
        line_index=16,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker C",
        content="Exactly. Space exploration is like stacking bricks",
        line_index=17,
    ),
)

SPACEX_DISCUSSION = MultiSpeakerFixture(
    name="spacex_discussion",
    description="Three colleagues discussing a SpaceX launch with technical details",
    num_speakers=3,
    input_text=_SPACEX_INPUT_TEXT,
    expected_lines=_SPACEX_EXPECTED_LINES,
    characteristics=(
        "Names mentioned in dialogue (Devin, Chris) but not speaker labels",
        "Natural conversational flow with varied sentence lengths",
        "Technical vocabulary and domain-specific terms",
        "Questions directed at specific individuals",
        "Acknowledgments and responses to previous statements",
    ),
)


# =============================================================================
# Generic 3-Speaker Meeting Fixture
# =============================================================================

_GENERIC_MEETING_INPUT = """Welcome everyone to the quarterly review meeting. Thanks for organizing this. Yes, thank you so much. No problem. Let's start with introductions. You both know me. I'm Peter Parker, and I thought it would be great for you two to meet. Who wants to go first? Sure, I'll go first. Thanks Frank, go ahead. Ok. My name is Frank Oz, and I like puppets. Thanks Frank. Fred? Oh yes, I'm Fred Flintstone. Great. Thank you both for joining us today."""  # noqa: E501

_GENERIC_MEETING_EXPECTED = (
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Welcome everyone to the quarterly review meeting",
        line_index=0,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker B",
        content="Thanks for organizing this",
        line_index=1,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker C",
        content="Yes, thank you so much",
        line_index=2,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="I'm Peter Parker",
        line_index=3,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker B",
        content="Sure, I'll go first",
        line_index=4,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Thanks Frank, go ahead",
        line_index=5,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker B",
        content="My name is Frank Oz",
        line_index=6,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Thanks Frank. Fred?",
        line_index=7,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker C",
        content="Oh yes, I'm Fred Flintstone",
        line_index=8,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Great. Thank you both",
        line_index=9,
    ),
)

GENERIC_MEETING_3SPEAKER = MultiSpeakerFixture(
    name="generic_meeting_3speaker",
    description="Business meeting with introductions and identity-aware constraints",
    num_speakers=3,
    input_text=_GENERIC_MEETING_INPUT,
    expected_lines=_GENERIC_MEETING_EXPECTED,
    characteristics=(
        "Self-identification patterns (I'm X, My name is Y)",
        "Addressing others by name (Thanks Frank, Fred?)",
        "Meeting organizer pattern (first speaker opens and closes)",
        "Acknowledgments and gratitude expressions",
        "Question-answer turn-taking",
    ),
)


# =============================================================================
# 4-Speaker Panel Discussion Fixture
# =============================================================================

_PANEL_DISCUSSION_INPUT = """Good morning everyone. Welcome to today's panel on AI ethics. Thank you for having us. It's a pleasure to be here. I'm excited to discuss this important topic. Let me start with the first question. What are the key ethical considerations for AI development? I believe transparency is fundamental. Without it, we can't build trust. I agree, but I'd add accountability. Who is responsible when AI fails? That's a great point. Both transparency and accountability are necessary. And I think we need to consider fairness too. AI systems can perpetuate biases. Yes, absolutely. Bias in AI is a critical concern. We've seen many examples of this. Can you give us a specific example? Sure. Consider hiring algorithms that discriminate based on historical data. Excellent point. Any other concerns? Privacy is huge. AI systems collect vast amounts of personal data. I completely agree. Data privacy must be protected. Thank you all for these insights. Let's open it up for questions."""  # noqa: E501

_PANEL_DISCUSSION_EXPECTED = (
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Good morning everyone. Welcome to today's panel",
        line_index=0,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker B",
        content="Thank you for having us",
        line_index=1,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker C",
        content="It's a pleasure to be here",
        line_index=2,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker D",
        content="I'm excited to discuss this important topic",
        line_index=3,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Let me start with the first question",
        line_index=4,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker B",
        content="I believe transparency is fundamental",
        line_index=5,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker C",
        content="I agree, but I'd add accountability",
        line_index=6,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker D",
        content="That's a great point. Both transparency and accountability",
        line_index=7,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker B",
        content="And I think we need to consider fairness too",
        line_index=8,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker C",
        content="Yes, absolutely. Bias in AI is a critical concern",
        line_index=9,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Can you give us a specific example",
        line_index=10,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker B",
        content="Sure. Consider hiring algorithms",
        line_index=11,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Excellent point. Any other concerns",
        line_index=12,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker D",
        content="Privacy is huge. AI systems collect vast amounts",
        line_index=13,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker C",
        content="I completely agree. Data privacy must be protected",
        line_index=14,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Thank you all for these insights",
        line_index=15,
    ),
)

PANEL_DISCUSSION_4SPEAKER = MultiSpeakerFixture(
    name="panel_discussion_4speaker",
    description="AI ethics panel with moderator and three panelists",
    num_speakers=4,
    input_text=_PANEL_DISCUSSION_INPUT,
    expected_lines=_PANEL_DISCUSSION_EXPECTED,
    characteristics=(
        "Moderator role (Speaker A asks questions, controls flow)",
        "Building on previous points (I agree, but...)",
        "Academic/professional tone",
        "Question-answer format",
        "Agreement and acknowledgment patterns",
    ),
)


# =============================================================================
# Technical Team Standup Fixture (3 speakers)
# =============================================================================

_STANDUP_INPUT = """Alright, let's start standup. I'll go first. Yesterday I finished the API refactoring and started on the database migration. Today I'm continuing with the migration and will need to coordinate with Sarah on the schema changes. I'm blocked on the staging environment - it's been down since yesterday. Thanks for the update. Sarah, you're next. Sure. I completed the schema design and reviewed Dan's API changes. Today I'm implementing the new user table structure. I need to sync with Dan on those schema changes he mentioned. No blockers from my side. Great. Mike, what about you? Yesterday I fixed the authentication bug and deployed the hotfix to production. Today I'm starting on the password reset feature. I might need Sarah's help with the database queries later. Sounds good everyone. Let's sync up after standup about the schema changes."""  # noqa: E501

_STANDUP_EXPECTED = (
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Alright, let's start standup. I'll go first",
        line_index=0,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Yesterday I finished the API refactoring",
        line_index=1,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Thanks for the update. Sarah, you're next",
        line_index=2,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker B",
        content="Sure. I completed the schema design",
        line_index=3,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Great. Mike, what about you",
        line_index=4,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker C",
        content="Yesterday I fixed the authentication bug",
        line_index=5,
    ),
    ExpectedSpeakerLine(
        speaker="Speaker A",
        content="Sounds good everyone. Let's sync up after standup",
        line_index=6,
    ),
)

TEAM_STANDUP_3SPEAKER = MultiSpeakerFixture(
    name="team_standup_3speaker",
    description="Technical team standup meeting with structured updates",
    num_speakers=3,
    input_text=_STANDUP_INPUT,
    expected_lines=_STANDUP_EXPECTED,
    characteristics=(
        "Structured format (yesterday, today, blockers)",
        "Addressing team members by name (Sarah, Mike)",
        "Meeting lead pattern (Speaker A facilitates)",
        "Cross-references between speakers",
        "Short, focused status updates",
    ),
)


# =============================================================================
# Fixture Collection for Easy Access
# =============================================================================

ALL_3SPEAKER_FIXTURES = (
    SPACEX_DISCUSSION,
    GENERIC_MEETING_3SPEAKER,
    TEAM_STANDUP_3SPEAKER,
)

ALL_4SPEAKER_FIXTURES = (PANEL_DISCUSSION_4SPEAKER,)

ALL_MULTI_SPEAKER_FIXTURES = ALL_3SPEAKER_FIXTURES + ALL_4SPEAKER_FIXTURES


def get_fixture_by_name(name: str) -> MultiSpeakerFixture | None:
    """Retrieve a fixture by its name.

    Args:
        name: The fixture name to look up

    Returns:
        The matching fixture, or None if not found
    """
    for fixture in ALL_MULTI_SPEAKER_FIXTURES:
        if fixture.name == name:
            return fixture
    return None

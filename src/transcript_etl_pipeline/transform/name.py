"""Name parsing and representation for speaker identification.

This module provides structured name handling with support for:
- First and last names
- Middle initials
- Multiple last names (e.g., "Garcia Rodriguez")
- Hyphenated names (e.g., "Anne-Marie")
- Name variant matching (e.g., "Dan" matches "Daniel", "Rob" matches "Robert")
"""

from dataclasses import dataclass, field
from typing import ClassVar

__all__ = ["Name"]


@dataclass(frozen=True)
class Name:
    """Structured representation of a person's name.

    Attributes:
        first_name: First name (required)
        last_name: List of last name components (can be empty for single-name)
        middle_initial: Optional middle initial (without period)
    """

    first_name: str
    last_name: list[str] = field(default_factory=lambda: [])
    middle_initial: str | None = None

    # Known shortened name variants
    _SHORTENED_VARIANTS: ClassVar[dict[str, set[str]]] = {
        # Full name -> shortened variants
        "daniel": {"dan", "danny"},
        "robert": {"rob", "bob", "bobby"},
        "william": {"will", "bill", "billy"},
        "richard": {"rich", "rick", "dick"},
        "michael": {"mike", "mikey"},
        "christopher": {"chris"},
        "matthew": {"matt"},
        "anthony": {"tony"},
        "andrew": {"andy", "drew"},
        "nicholas": {"nick"},
        "alexander": {"alex"},
        "benjamin": {"ben"},
        "jonathan": {"jon"},
        "joseph": {"joe"},
        "thomas": {"tom", "tommy"},
        "charles": {"charlie", "chuck"},
        "elizabeth": {"liz", "beth", "betty"},
        "katherine": {"kate", "katie", "kathy"},
        "jennifer": {"jen", "jenny"},
        "patricia": {"pat", "patty"},
        "margaret": {"maggie", "peg", "meg"},
        "rebecca": {"becca", "becky"},
        "stephanie": {"steph"},
        "samantha": {"sam"},
        "christine": {"chris"},
        "victoria": {"vicky", "tori"},
    }

    # Reverse mapping: shortened -> full names
    _FULL_FROM_SHORT: ClassVar[dict[str, set[str]]] = {}

    @classmethod
    def _build_reverse_mapping(cls) -> None:
        """Build reverse mapping of shortened names to full names."""
        if cls._FULL_FROM_SHORT:
            return  # Already built

        for full_name, variants in cls._SHORTENED_VARIANTS.items():
            for variant in variants:
                if variant not in cls._FULL_FROM_SHORT:
                    cls._FULL_FROM_SHORT[variant] = set()
                cls._FULL_FROM_SHORT[variant].add(full_name)

    def __post_init__(self) -> None:
        """Validate name components."""
        if not self.first_name or not self.first_name.strip():
            raise ValueError("first_name cannot be empty")

        # Ensure class-level reverse mapping is built
        Name._build_reverse_mapping()

    @property
    def full_name(self) -> str:
        """Get the full name as a string.

        Returns:
            Full name with first, optional middle initial, and last name(s)
        """
        parts = [self.first_name]

        if self.middle_initial:
            parts.append(f"{self.middle_initial}.")

        if self.last_name:
            parts.extend(self.last_name)

        return " ".join(parts)

    @property
    def shortened_variants(self) -> set[str]:
        """Get all known shortened variants of the first name.

        Returns:
            Set of shortened name variants (e.g., {"Dan", "Danny"} for "Daniel")
            Includes the original first name
        """
        variants = {self.first_name}
        first_lower = self.first_name.lower()

        # Add known shortened variants if this is a full name
        if first_lower in self._SHORTENED_VARIANTS:
            variants.update(v.capitalize() for v in self._SHORTENED_VARIANTS[first_lower])

        # Add full names if this is a shortened variant
        if first_lower in self._FULL_FROM_SHORT:
            variants.update(v.capitalize() for v in self._FULL_FROM_SHORT[first_lower])

        return variants

    def matches(self, other: object) -> bool:
        """Check if this name matches another name.

        Matching rules:
        - First names match if they are variants of each other
        - Last names must match exactly (if both have last names)
        - Middle initials are ignored for matching

        Args:
            other: Another Name object to compare

        Returns:
            True if names match according to the rules above
        """
        if not isinstance(other, Name):
            return False

        # Check if first names match (via variants)
        first_match = self.first_name.lower() in {
            v.lower() for v in other.shortened_variants
        } or other.first_name.lower() in {v.lower() for v in self.shortened_variants}

        if not first_match:
            return False

        # If both have last names, they must match exactly
        if self.last_name and other.last_name:
            return [ln.lower() for ln in self.last_name] == [ln.lower() for ln in other.last_name]

        # If only one has a last name, first name match is sufficient
        return True

    def __eq__(self, other: object) -> bool:
        """Check exact equality of names.

        Args:
            other: Object to compare

        Returns:
            True if all components match exactly
        """
        if not isinstance(other, Name):
            return NotImplemented

        return (
            self.first_name.lower() == other.first_name.lower()
            and [ln.lower() for ln in self.last_name] == [ln.lower() for ln in other.last_name]
            and (self.middle_initial or "").lower() == (other.middle_initial or "").lower()
        )

    def __hash__(self) -> int:
        """Hash for use in sets and dicts.

        Returns:
            Hash value based on normalized name components
        """
        return hash(
            (
                self.first_name.lower(),
                tuple(ln.lower() for ln in self.last_name),
                (self.middle_initial or "").lower(),
            )
        )

    @staticmethod
    def from_string(name_str: str) -> "Name":
        """Parse a name string into a Name object.

        Patterns supported:
        - "John" -> Name(first_name="John")
        - "John Smith" -> Name(first_name="John", last_name=["Smith"])
        - "John A Smith" -> Name(first_name="John", middle_initial="A", last_name=["Smith"])
        - "John Smith Jones" -> Name(first_name="John", last_name=["Smith", "Jones"])
        - "Anne-Marie" -> Name(first_name="Anne-Marie") (hyphenated treated as single token)

        Args:
            name_str: Name string to parse

        Returns:
            Parsed Name object

        Raises:
            ValueError: If name_str is empty or has more than 3 tokens
        """
        if not name_str or not name_str.strip():
            raise ValueError("name_str cannot be empty")

        # Tokenize by spaces, treating hyphenated names as single tokens
        tokens = [t.strip() for t in name_str.strip().split() if t.strip()]

        if len(tokens) == 0:
            raise ValueError("name_str must contain at least one token")
        if len(tokens) > 3:
            raise ValueError(f"name_str cannot have more than 3 tokens: {name_str}")

        # Use name_resolution to parse tokens
        return Name._name_resolution(tokens)

    @staticmethod
    def _name_resolution(tokens: list[str]) -> "Name":
        """Resolve name tokens into Name components.

        Args:
            tokens: List of 1-3 name tokens

        Returns:
            Name object with resolved components

        Raises:
            ValueError: If token count is invalid
        """
        if len(tokens) == 1:
            # Single token: first name only
            return Name(first_name=tokens[0])

        elif len(tokens) == 2:
            # Two tokens: first name + last name
            return Name(first_name=tokens[0], last_name=[tokens[1]])

        elif len(tokens) == 3:
            # Three tokens: Check if token2 is middle initial or first last name
            # Middle initial: single letter optionally followed by period
            token2_cleaned = tokens[1].rstrip(".")

            if len(token2_cleaned) == 1:
                # Token 2 is middle initial
                return Name(
                    first_name=tokens[0], middle_initial=token2_cleaned, last_name=[tokens[2]]
                )
            else:
                # Token 2 is first last name, token 3 is second last name
                # Prefer double last name pattern for multi-letter tokens
                return Name(first_name=tokens[0], last_name=[tokens[1], tokens[2]])

        else:
            raise ValueError(f"Invalid token count: {len(tokens)}")

    def __str__(self) -> str:
        """String representation of the name.

        Returns:
            Full name string
        """
        return self.full_name

    def __repr__(self) -> str:
        """Detailed representation for debugging.

        Returns:
            Repr string showing all components
        """
        parts = [f"first_name={self.first_name!r}"]
        if self.last_name:
            parts.append(f"last_name={self.last_name!r}")
        if self.middle_initial:
            parts.append(f"middle_initial={self.middle_initial!r}")
        return f"Name({', '.join(parts)})"

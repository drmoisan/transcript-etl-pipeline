"""Tests for Name class and name parsing functionality."""

import pytest

from transcript_etl_pipeline.transform.name import Name


class TestNameConstruction:
    """Test Name object construction."""

    def test_first_name_only(self) -> None:
        """Test creating name with only first name."""
        name = Name(first_name="John")
        assert name.first_name == "John"
        assert name.last_name == []
        assert name.middle_initial is None
        assert name.full_name == "John"

    def test_first_and_last_name(self) -> None:
        """Test creating name with first and last name."""
        name = Name(first_name="John", last_name=["Smith"])
        assert name.first_name == "John"
        assert name.last_name == ["Smith"]
        assert name.full_name == "John Smith"

    def test_double_last_name(self) -> None:
        """Test creating name with double last name."""
        name = Name(first_name="Maria", last_name=["Garcia", "Rodriguez"])
        assert name.first_name == "Maria"
        assert name.last_name == ["Garcia", "Rodriguez"]
        assert name.full_name == "Maria Garcia Rodriguez"

    def test_with_middle_initial(self) -> None:
        """Test creating name with middle initial."""
        name = Name(first_name="John", middle_initial="A", last_name=["Smith"])
        assert name.first_name == "John"
        assert name.middle_initial == "A"
        assert name.last_name == ["Smith"]
        assert name.full_name == "John A. Smith"

    def test_empty_first_name_raises(self) -> None:
        """Test that empty first name raises ValueError."""
        with pytest.raises(ValueError, match="first_name cannot be empty"):
            Name(first_name="")


class TestFromString:
    """Test parsing names from strings."""

    def test_single_token(self) -> None:
        """Test parsing single name token."""
        name = Name.from_string("John")
        assert name.first_name == "John"
        assert name.last_name == []
        assert name.middle_initial is None

    def test_two_tokens(self) -> None:
        """Test parsing first and last name."""
        name = Name.from_string("John Smith")
        assert name.first_name == "John"
        assert name.last_name == ["Smith"]
        assert name.middle_initial is None

    def test_three_tokens_with_middle_initial(self) -> None:
        """Test parsing first, middle initial, and last name."""
        name = Name.from_string("John A Smith")
        assert name.first_name == "John"
        assert name.middle_initial == "A"
        assert name.last_name == ["Smith"]

    def test_three_tokens_with_middle_initial_period(self) -> None:
        """Test parsing middle initial with period."""
        name = Name.from_string("John A. Smith")
        assert name.first_name == "John"
        assert name.middle_initial == "A"
        assert name.last_name == ["Smith"]

    def test_three_tokens_double_last_name(self) -> None:
        """Test parsing double last name (multi-letter middle token)."""
        name = Name.from_string("Maria Garcia Rodriguez")
        assert name.first_name == "Maria"
        assert name.last_name == ["Garcia", "Rodriguez"]
        assert name.middle_initial is None

    def test_hyphenated_first_name(self) -> None:
        """Test hyphenated names are treated as single token."""
        name = Name.from_string("Anne-Marie")
        assert name.first_name == "Anne-Marie"
        assert name.last_name == []

    def test_hyphenated_last_name(self) -> None:
        """Test hyphenated last name."""
        name = Name.from_string("John Smith-Jones")
        assert name.first_name == "John"
        assert name.last_name == ["Smith-Jones"]

    def test_empty_string_raises(self) -> None:
        """Test empty string raises ValueError."""
        with pytest.raises(ValueError, match="name_str cannot be empty"):
            Name.from_string("")

    def test_whitespace_only_raises(self) -> None:
        """Test whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="name_str cannot be empty"):
            Name.from_string("   ")

    def test_too_many_tokens_raises(self) -> None:
        """Test more than 3 tokens raises ValueError."""
        with pytest.raises(ValueError, match="cannot have more than 3 tokens"):
            Name.from_string("John A B Smith")


class TestShortenedVariants:
    """Test shortened name variant generation."""

    def test_daniel_variants(self) -> None:
        """Test variants for Daniel."""
        name = Name(first_name="Daniel")
        variants = name.shortened_variants
        assert "Daniel" in variants
        assert "Dan" in variants
        assert "Danny" in variants

    def test_dan_variants_includes_full(self) -> None:
        """Test Dan includes Daniel as variant."""
        name = Name(first_name="Dan")
        variants = name.shortened_variants
        assert "Dan" in variants
        assert "Daniel" in variants

    def test_robert_variants(self) -> None:
        """Test variants for Robert."""
        name = Name(first_name="Robert")
        variants = name.shortened_variants
        assert "Robert" in variants
        assert "Rob" in variants
        assert "Bob" in variants
        assert "Bobby" in variants

    def test_uncommon_name_no_variants(self) -> None:
        """Test uncommon name has no additional variants."""
        name = Name(first_name="Zebediah")
        variants = name.shortened_variants
        assert variants == {"Zebediah"}

    def test_last_name_doesnt_affect_variants(self) -> None:
        """Test last name doesn't affect first name variants."""
        name = Name(first_name="Daniel", last_name=["Smith"])
        variants = name.shortened_variants
        assert "Dan" in variants
        assert "Danny" in variants
        # Should not include last name
        assert "Smith" not in variants


class TestMatches:
    """Test name matching functionality."""

    def test_exact_match_first_name_only(self) -> None:
        """Test exact match with first name only."""
        name1 = Name(first_name="John")
        name2 = Name(first_name="John")
        assert name1.matches(name2)
        assert name2.matches(name1)

    def test_exact_match_first_and_last(self) -> None:
        """Test exact match with first and last name."""
        name1 = Name(first_name="John", last_name=["Smith"])
        name2 = Name(first_name="John", last_name=["Smith"])
        assert name1.matches(name2)

    def test_variant_match_same_full_name(self) -> None:
        """Test variant matching (Dan vs Daniel) with same last name."""
        name1 = Name(first_name="Dan", last_name=["Moisan"])
        name2 = Name(first_name="Daniel", last_name=["Moisan"])
        assert name1.matches(name2)
        assert name2.matches(name1)

    def test_variant_match_first_name_only(self) -> None:
        """Test variant matching with first name only."""
        name1 = Name(first_name="Rob")
        name2 = Name(first_name="Robert")
        assert name1.matches(name2)
        assert name2.matches(name1)

    def test_variant_match_one_with_last_name(self) -> None:
        """Test variant match when only one has last name."""
        name1 = Name(first_name="Dan")
        name2 = Name(first_name="Daniel", last_name=["Moisan"])
        assert name1.matches(name2)
        assert name2.matches(name1)

    def test_different_last_names_no_match(self) -> None:
        """Test different last names prevent match."""
        name1 = Name(first_name="John", last_name=["Smith"])
        name2 = Name(first_name="John", last_name=["Jones"])
        assert not name1.matches(name2)

    def test_different_first_names_no_match(self) -> None:
        """Test completely different first names don't match."""
        name1 = Name(first_name="John", last_name=["Smith"])
        name2 = Name(first_name="Alice", last_name=["Smith"])
        assert not name1.matches(name2)

    def test_middle_initial_ignored(self) -> None:
        """Test middle initial is ignored for matching."""
        name1 = Name(first_name="John", middle_initial="A", last_name=["Smith"])
        name2 = Name(first_name="John", last_name=["Smith"])
        assert name1.matches(name2)
        assert name2.matches(name1)

    def test_case_insensitive_matching(self) -> None:
        """Test matching is case-insensitive."""
        name1 = Name(first_name="john", last_name=["smith"])
        name2 = Name(first_name="JOHN", last_name=["SMITH"])
        assert name1.matches(name2)

    def test_matches_with_non_name_returns_false(self) -> None:
        """Test matches returns False for non-Name objects."""
        name = Name(first_name="John")
        assert not name.matches("John")  # type: ignore[arg-type]
        assert not name.matches(123)  # type: ignore[arg-type]


class TestEquality:
    """Test name equality (exact match)."""

    def test_exact_equality_first_name_only(self) -> None:
        """Test exact equality with first name only."""
        name1 = Name(first_name="John")
        name2 = Name(first_name="John")
        assert name1 == name2

    def test_exact_equality_with_last_name(self) -> None:
        """Test exact equality with last name."""
        name1 = Name(first_name="John", last_name=["Smith"])
        name2 = Name(first_name="John", last_name=["Smith"])
        assert name1 == name2

    def test_variant_not_equal(self) -> None:
        """Test variants are not considered equal (only matches)."""
        name1 = Name(first_name="Dan")
        name2 = Name(first_name="Daniel")
        assert name1 != name2  # Exact equality requires same spelling

    def test_case_insensitive_equality(self) -> None:
        """Test equality is case-insensitive."""
        name1 = Name(first_name="john", last_name=["smith"])
        name2 = Name(first_name="JOHN", last_name=["SMITH"])
        assert name1 == name2

    def test_different_names_not_equal(self) -> None:
        """Test different names are not equal."""
        name1 = Name(first_name="John")
        name2 = Name(first_name="Alice")
        assert name1 != name2


class TestHashing:
    """Test name hashing for sets and dicts."""

    def test_can_add_to_set(self) -> None:
        """Test names can be added to sets."""
        name1 = Name(first_name="John", last_name=["Smith"])
        name2 = Name(first_name="Alice", last_name=["Jones"])
        names = {name1, name2}
        assert len(names) == 2

    def test_duplicate_names_in_set(self) -> None:
        """Test duplicate names are de-duplicated in sets."""
        name1 = Name(first_name="John", last_name=["Smith"])
        name2 = Name(first_name="John", last_name=["Smith"])
        names = {name1, name2}
        assert len(names) == 1

    def test_can_use_as_dict_key(self) -> None:
        """Test names can be used as dictionary keys."""
        name = Name(first_name="John", last_name=["Smith"])
        mapping = {name: "Speaker A"}
        assert mapping[name] == "Speaker A"


class TestStringRepresentation:
    """Test string representations."""

    def test_str_first_name_only(self) -> None:
        """Test string representation with first name only."""
        name = Name(first_name="John")
        assert str(name) == "John"

    def test_str_first_and_last(self) -> None:
        """Test string representation with first and last name."""
        name = Name(first_name="John", last_name=["Smith"])
        assert str(name) == "John Smith"

    def test_str_with_middle_initial(self) -> None:
        """Test string representation with middle initial."""
        name = Name(first_name="John", middle_initial="A", last_name=["Smith"])
        assert str(name) == "John A. Smith"

    def test_repr_shows_components(self) -> None:
        """Test repr shows all components."""
        name = Name(first_name="John", middle_initial="A", last_name=["Smith"])
        repr_str = repr(name)
        assert "first_name='John'" in repr_str
        assert "middle_initial='A'" in repr_str
        assert "last_name=['Smith']" in repr_str


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_single_letter_first_name(self) -> None:
        """Test single-letter first name is allowed."""
        name = Name(first_name="J")
        assert name.first_name == "J"

    def test_multiple_spaces_in_from_string(self) -> None:
        """Test multiple spaces are handled correctly."""
        name = Name.from_string("John   Smith")
        assert name.first_name == "John"
        assert name.last_name == ["Smith"]

    def test_leading_trailing_spaces(self) -> None:
        """Test leading/trailing spaces are stripped."""
        name = Name.from_string("  John Smith  ")
        assert name.first_name == "John"
        assert name.last_name == ["Smith"]

    def test_frozen_dataclass(self) -> None:
        """Test Name is frozen (immutable)."""
        name = Name(first_name="John")
        with pytest.raises(AttributeError):
            name.first_name = "Jane"  # type: ignore[misc]

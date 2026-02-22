import string

import pytest

from nqcc import ConstantToken, IdentifierToken


class TestIdentifierToken:
    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("nxt_char", ["_", *string.ascii_letters])
    def test_allowed_first_characters(self, position, nxt_char):
        target = IdentifierToken()
        result = target.append(nxt_char, position)
        assert result, "Should accept character at start"
        assert target.start_position == position
        assert target.value == nxt_char

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize(
        "nxt_char", {*string.digits, *string.punctuation, *string.whitespace} - {"_"}
    )
    def test_disallowed_first_characters(self, position, nxt_char):
        # Slightly ugly parameter list because underscores are allowed....
        target = IdentifierToken()
        result = target.append(nxt_char, position)
        assert not result, "Should NOT accept character at start"
        assert target.start_position == -1
        assert target.value == ""

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", ["A", "b"])
    @pytest.mark.parametrize("nxt_char", ["_", *string.ascii_letters, *string.digits])
    def test_allowed_second_characters(self, position, first_char, nxt_char):
        target = IdentifierToken()
        _ = target.append(first_char, position)
        result = target.append(nxt_char, position + 1)
        assert result, "Should accept character after start"
        assert target.start_position == position
        assert target.value == f"{first_char}{nxt_char}"

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", ["A", "b"])
    @pytest.mark.parametrize("nxt_char", {*string.punctuation, *string.whitespace} - {"_"})
    def test_disallowed_second_characters(self, position, first_char, nxt_char):
        target = IdentifierToken()
        _ = target.append(first_char, position)
        result = target.append(nxt_char, position + 1)
        assert not result, "Should NOT accept character after start"
        assert target.start_position == position
        assert target.value == f"{first_char}"


class TestConstantToken:
    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("nxt_char", string.digits)
    def test_allowed_first_characters(self, position, nxt_char):
        target = ConstantToken()
        result = target.append(nxt_char, position)
        assert result, "Should accept character at start"
        assert target.start_position == position
        assert target.value == nxt_char

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize(
        "nxt_char", [*string.ascii_letters, *string.punctuation, *string.whitespace]
    )
    def test_disallowed_first_characters(self, position, nxt_char):
        target = ConstantToken()
        result = target.append(nxt_char, position)
        assert not result, "Should NOT accept character at start"
        assert target.start_position == -1
        assert target.value == ""

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", ["1", "0"])
    @pytest.mark.parametrize("nxt_char", string.digits)
    def test_allowed_second_characters(self, position, first_char, nxt_char):
        target = ConstantToken()
        _ = target.append(first_char, position)
        result = target.append(nxt_char, position + 1)
        assert result, "Should accept character after start"
        assert target.start_position == position
        assert target.value == f"{first_char}{nxt_char}"

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", ["1", "0"])
    @pytest.mark.parametrize(
        "nxt_char", [*string.ascii_letters, *string.punctuation, *string.whitespace]
    )
    def test_disallowed_second_characters(self, position, first_char, nxt_char):
        target = ConstantToken()
        _ = target.append(first_char, position)
        result = target.append(nxt_char, position + 1)
        assert not result, "Should NOT accept character after start"
        assert target.start_position == position
        assert target.value == f"{first_char}"

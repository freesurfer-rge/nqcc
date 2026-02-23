import string

import pytest

from nqcc.lexer import (
    AppendResult,
    CloseBraceToken,
    CloseParenToken,
    ConstantIntegerToken,
    IdentifierToken,
    KeywordToken,
    OpenBraceToken,
    OpenParenToken,
    SemicolonToken,
    WhitespaceToken,
)

_WORD_CHARS = {c for c in string.printable if (c.isalnum() or c=="_")}
_NONWORD_CHARS = {*string.printable} - _WORD_CHARS

class TestIdentifierToken:
    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("nxt_char", ["_", *string.ascii_letters])
    def test_allowed_first_characters(self, position, nxt_char):
        target = IdentifierToken()
        assert not target.is_valid
        assert target.is_appendable
        result = target.try_append(nxt_char, position)
        assert result == AppendResult.ACCEPTED, "Should accept character at start"
        assert target.start_position == position
        assert target.value == nxt_char
        assert target.is_valid
        assert target.is_appendable

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize(
        "nxt_char", _NONWORD_CHARS
    )
    def test_disallowed_first_characters(self, position, nxt_char):
        # Slightly ugly parameter list because underscores are allowed....
        target = IdentifierToken()
        assert not target.is_valid
        assert target.is_appendable
        result = target.try_append(nxt_char, position)
        assert result == AppendResult.REJECTED, "Should NOT accept character at start"
        assert target.start_position == -1
        assert target.value == ""
        assert not target.is_valid
        assert target.is_appendable

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", ["A", "b"])
    @pytest.mark.parametrize("nxt_char", _WORD_CHARS)
    def test_allowed_second_characters(self, position, first_char, nxt_char):
        target = IdentifierToken()
        assert not target.is_valid
        assert target.is_appendable
        _ = target.try_append(first_char, position)
        result = target.try_append(nxt_char, position + 1)
        assert result == AppendResult.ACCEPTED, "Should accept character after start"
        assert target.start_position == position
        assert target.value == f"{first_char}{nxt_char}"
        assert target.is_valid
        assert target.is_appendable

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", ["A", "b"])
    @pytest.mark.parametrize("nxt_char", _NONWORD_CHARS)
    def test_disallowed_second_characters(self, position, first_char, nxt_char):
        target = IdentifierToken()
        assert not target.is_valid
        assert target.is_appendable
        _ = target.try_append(first_char, position)
        result = target.try_append(nxt_char, position + 1)
        assert result == AppendResult.CAN_FOLLOW, "Should NOT accept character after start"
        assert target.start_position == position
        assert target.value == f"{first_char}"
        assert target.is_valid
        assert target.is_appendable

class TestConstantIntegerToken:
    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("nxt_char", string.digits)
    def test_allowed_first_characters(self, position, nxt_char):
        target = ConstantIntegerToken()
        assert not target.is_valid
        assert target.is_appendable
        result = target.try_append(nxt_char, position)
        assert result == AppendResult.ACCEPTED, "Should accept character at start"
        assert target.start_position == position
        assert target.value == nxt_char
        assert target.is_valid
        assert target.is_appendable

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize(
        "nxt_char", {*string.printable} - {*string.digits}
    )
    def test_disallowed_first_characters(self, position, nxt_char):
        target = ConstantIntegerToken()
        assert not target.is_valid
        assert target.is_appendable
        result = target.try_append(nxt_char, position)
        assert result == AppendResult.REJECTED, "Should NOT accept character at start"
        assert target.start_position == -1
        assert target.value == ""
        assert not target.is_valid
        assert target.is_appendable

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", ["1", "0"])
    @pytest.mark.parametrize("nxt_char", string.digits)
    def test_allowed_second_characters(self, position, first_char, nxt_char):
        target = ConstantIntegerToken()
        assert not target.is_valid
        assert target.is_appendable
        _ = target.try_append(first_char, position)
        result = target.try_append(nxt_char, position + 1)
        assert result == AppendResult.ACCEPTED, "Should accept character after start"
        assert target.start_position == position
        assert target.value == f"{first_char}{nxt_char}"
        assert target.is_valid
        assert target.is_appendable

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", ["1", "0"])
    @pytest.mark.parametrize(
        "nxt_char", _WORD_CHARS - {*string.digits}
    )
    def test_disallowed_second_characters_reject(self, position, first_char, nxt_char):
        target = ConstantIntegerToken()
        assert not target.is_valid
        assert target.is_appendable
        _ = target.try_append(first_char, position)
        result = target.try_append(nxt_char, position + 1)
        assert result == AppendResult.REJECTED, "Should NOT accept character after start"
        assert target.start_position == position
        assert target.value == f"{first_char}"
        assert target.is_valid
        assert target.is_appendable

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", ["1", "0"])
    @pytest.mark.parametrize(
        "nxt_char", _NONWORD_CHARS
    )
    def test_disallowed_second_characters_can_follow(self, position, first_char, nxt_char):
        target = ConstantIntegerToken()
        assert not target.is_valid
        assert target.is_appendable
        _ = target.try_append(first_char, position)
        result = target.try_append(nxt_char, position + 1)
        assert result == AppendResult.CAN_FOLLOW, "Should NOT accept character after start"
        assert target.start_position == position
        assert target.value == f"{first_char}"
        assert target.is_valid
        assert target.is_appendable


class TestWhitespaceToken:
    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", string.whitespace)
    @pytest.mark.parametrize("nxt_char", string.whitespace)
    def test_allowed_chars(self, first_char, nxt_char, position):
        target = WhitespaceToken()
        assert not target.is_valid
        assert target.is_appendable
        result = target.try_append(first_char, position)
        assert result == AppendResult.ACCEPTED, f"Failed to append '{repr(first_char)}'"
        assert target.start_position == position

        result = target.try_append(nxt_char, position + 1)
        assert result == AppendResult.ACCEPTED, f"Failed to append '{repr(nxt_char)}'"
        assert target.start_position == position

        assert target.value == f"{first_char}{nxt_char}"
        assert target.is_valid
        assert target.is_appendable

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("bad_char", {*string.printable} - {*string.whitespace})
    def test_disallowed_first_char(self, bad_char, position):
        target = WhitespaceToken()
        assert not target.is_valid
        assert target.is_appendable
        result = target.try_append(bad_char, position)
        assert result == AppendResult.REJECTED, f"Unexpected append: {bad_char}"
        assert target.start_position == -1
        assert not target.value
        assert not target.is_valid
        assert target.is_appendable

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", {*string.whitespace})
    @pytest.mark.parametrize("bad_char", {*string.printable} - {*string.whitespace})
    def test_disallowed_second_char(self, first_char, bad_char, position):
        target = WhitespaceToken()
        assert not target.is_valid
        assert target.is_appendable
        result = target.try_append(first_char, position)
        assert result == AppendResult.ACCEPTED
        result = target.try_append(bad_char, position+1)
        assert result == AppendResult.CAN_FOLLOW, f"Unexpected append: {bad_char}"
        assert target.start_position == position
        assert target.value == first_char
        assert target.is_valid
        assert target.is_appendable


TEST_KEYWORDS = {"int", "void", "return"}


class TestKeywordToken:
    @pytest.mark.parametrize("keyword", TEST_KEYWORDS)
    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize(
        "nxt_char", [*string.ascii_letters, *string.punctuation, *string.whitespace]
    )
    def test_allowed_keywords(self, keyword, position, nxt_char):
        target = KeywordToken()
        assert target.is_appendable

        # The valid portion
        for i, c in enumerate(keyword):
            assert not target.is_valid
            assert target.is_appendable
            result = target.try_append(c, position + i)
            assert result == AppendResult.ACCEPTED, f"Failed to append {c}"
            assert target.start_position == position
        assert target.is_valid
        assert target.value == keyword
        assert not target.is_appendable

        # Try to append an invalid character
        result = target.try_append(nxt_char, position + len(keyword))
        assert result == AppendResult.REJECTED, f"Unexpected append {c}"
        assert target.value == keyword
        assert target.is_valid
        assert not target.is_appendable


class TestSingleCharacterTokens:
    @pytest.mark.parametrize(
        ("tokenClass", "tok"),
        [
            (OpenParenToken, "("),
            (CloseParenToken, ")"),
            (OpenBraceToken, "{"),
            (CloseBraceToken, "}"),
            (SemicolonToken, ";"),
        ],
    )
    @pytest.mark.parametrize("position", [0, 10])
    def test_allowed_chars(self, tokenClass, tok: str, position: int):
        target = tokenClass()
        assert target.is_appendable

        INVALID_FIRST_CHARS = {*string.printable} - {tok}
        for c in INVALID_FIRST_CHARS:
            result = target.try_append(c, position)
            assert result == AppendResult.REJECTED, f"Unexpected append: {c}"
            assert target.start_position == -1
            assert not target.is_valid
            assert target.is_appendable

        # Append the correct character
        result = target.try_append(tok, position)
        assert result == AppendResult.ACCEPTED, f"Failed to append {c}"
        assert target.start_position == position
        assert target.value == tok
        assert target.is_valid
        assert not target.is_appendable

        # Try to append another character
        for c in string.printable:
            result = target.try_append(c, position)
            assert result == AppendResult.CAN_FOLLOW, f"Unexpected append: {c}"
        assert target.start_position == position
        assert target.value == tok
        assert target.is_valid
        assert not target.is_appendable

import string

import pytest

from nqcc import (
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


class TestIdentifierToken:
    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("nxt_char", ["_", *string.ascii_letters])
    def test_allowed_first_characters(self, position, nxt_char):
        target = IdentifierToken()
        result = target.try_append(nxt_char, position)
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
        result = target.try_append(nxt_char, position)
        assert not result, "Should NOT accept character at start"
        assert target.start_position == -1
        assert target.value == ""

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", ["A", "b"])
    @pytest.mark.parametrize("nxt_char", ["_", *string.ascii_letters, *string.digits])
    def test_allowed_second_characters(self, position, first_char, nxt_char):
        target = IdentifierToken()
        _ = target.try_append(first_char, position)
        result = target.try_append(nxt_char, position + 1)
        assert result, "Should accept character after start"
        assert target.start_position == position
        assert target.value == f"{first_char}{nxt_char}"

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", ["A", "b"])
    @pytest.mark.parametrize("nxt_char", {*string.punctuation, *string.whitespace} - {"_"})
    def test_disallowed_second_characters(self, position, first_char, nxt_char):
        target = IdentifierToken()
        _ = target.try_append(first_char, position)
        result = target.try_append(nxt_char, position + 1)
        assert not result, "Should NOT accept character after start"
        assert target.start_position == position
        assert target.value == f"{first_char}"


class TestConstantIntegerToken:
    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("nxt_char", string.digits)
    def test_allowed_first_characters(self, position, nxt_char):
        target = ConstantIntegerToken()
        result = target.try_append(nxt_char, position)
        assert result, "Should accept character at start"
        assert target.start_position == position
        assert target.value == nxt_char

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize(
        "nxt_char", [*string.ascii_letters, *string.punctuation, *string.whitespace]
    )
    def test_disallowed_first_characters(self, position, nxt_char):
        target = ConstantIntegerToken()
        result = target.try_append(nxt_char, position)
        assert not result, "Should NOT accept character at start"
        assert target.start_position == -1
        assert target.value == ""

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", ["1", "0"])
    @pytest.mark.parametrize("nxt_char", string.digits)
    def test_allowed_second_characters(self, position, first_char, nxt_char):
        target = ConstantIntegerToken()
        _ = target.try_append(first_char, position)
        result = target.try_append(nxt_char, position + 1)
        assert result, "Should accept character after start"
        assert target.start_position == position
        assert target.value == f"{first_char}{nxt_char}"

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", ["1", "0"])
    @pytest.mark.parametrize(
        "nxt_char", [*string.ascii_letters, *string.punctuation, *string.whitespace]
    )
    def test_disallowed_second_characters(self, position, first_char, nxt_char):
        target = ConstantIntegerToken()
        _ = target.try_append(first_char, position)
        result = target.try_append(nxt_char, position + 1)
        assert not result, "Should NOT accept character after start"
        assert target.start_position == position
        assert target.value == f"{first_char}"


class TestWhitespaceToken:
    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("first_char", string.whitespace)
    @pytest.mark.parametrize("nxt_char", string.whitespace)
    def test_allowed_chars(self, first_char, nxt_char, position):
        target = WhitespaceToken()

        result = target.try_append(first_char, position)
        assert result, f"Failed to append '{repr(first_char)}'"
        assert target.start_position == position

        result = target.try_append(nxt_char, position + 1)
        assert result, f"Failed to append '{repr(nxt_char)}'"
        assert target.start_position == position

        assert target.value == f"{first_char}{nxt_char}"

    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize("bad_char", {*string.printable} - {*string.whitespace})
    def test_disallowed_char(self, bad_char, position):
        target = WhitespaceToken()

        result = target.try_append(bad_char, position)
        assert not result, f"Unexpected append: {bad_char}"
        assert target.start_position == -1
        assert not target.value


TEST_KEYWORDS = {"int", "void", "return"}


class TestKeywordToken:
    @pytest.mark.parametrize("keyword", TEST_KEYWORDS)
    @pytest.mark.parametrize("position", [0, 10])
    @pytest.mark.parametrize(
        "nxt_char", [*string.ascii_letters, *string.punctuation, *string.whitespace]
    )
    def test_allowed_keywords(self, keyword, position, nxt_char):
        target = KeywordToken()

        # The valid portion
        for i, c in enumerate(keyword):
            result = target.try_append(c, position + i)
            assert result, f"Failed to append {c}"
            assert target.start_position == position
        assert target.value == keyword

        # Try to append an invalid character
        result = target.try_append(nxt_char, position + len(keyword))
        assert not result, f"Unexpected append {c}"
        assert target.value == keyword


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

        INVALID_FIRST_CHARS = {*string.printable} - {tok}
        for c in INVALID_FIRST_CHARS:
            result = target.try_append(c, position)
            assert not result, f"Unexpected append: {c}"
            assert target.start_position == -1

        # Append the correct character
        result = target.try_append(tok, position)
        assert result, f"Failed to append {c}"
        assert target.start_position == position
        assert target.value == tok

        # Try to append another character
        for c in string.printable:
            result = target.try_append(c, position)
            assert not result, f"Unexpected append: {c}"
        assert target.start_position == position
        assert target.value == tok

import string

import pytest

from nqcc.lexer import (
    CloseBraceToken,
    CloseParenToken,
    ConstantIntegerToken,
    IdentifierToken,
    KeywordToken,
    Lexer,
    LexerError,
    OpenBraceToken,
    OpenParenToken,
    SemicolonToken,
    TokenItem,
    extract_tokens,
)


class TestLexer:
    def compare_tokens_without_position(self, expected: list[TokenItem], actual: list[TokenItem]):
        assert len(expected) == len(actual)

        for t_e, t_a in zip(expected, actual, strict=True):
            assert type(t_e) is type(t_a)
            assert t_e.value == t_a.value

    def test_smoke(self):
        target = Lexer()

        sample_string = "  int main( void )"

        for ch in sample_string:
            target.push_character(ch)
        target.character_stream_done()

        final_tokens = target.completed_token_list
        assert len(final_tokens) == 5

        expected_tokens = [
            KeywordToken(start_position=2, value="int"),
            IdentifierToken(start_position=6, value="main"),
            OpenParenToken(start_position=10, value="("),
            KeywordToken(start_position=12, value="void"),
            CloseParenToken(start_position=17, value=")"),
        ]
        assert final_tokens == expected_tokens

    def test_token_at_start(self):
        target = Lexer()
        sample_string = "123"
        for ch in sample_string:
            target.push_character(ch)
        target.character_stream_done()

        final_tokens = target.completed_token_list
        assert len(final_tokens) == 1
        assert final_tokens[0] == ConstantIntegerToken(start_position=0, value="123")

    @pytest.mark.parametrize("space_replace", {*string.whitespace, "  "})
    def test_simple_program(self, space_replace: str):
        target = Lexer()

        program_str = "int my_func ( void ) { return 2; }"
        program_str = program_str.replace(" ", space_replace)

        expected_tokens = [
            KeywordToken(value="int"),
            IdentifierToken(value="my_func"),
            OpenParenToken(value="("),
            KeywordToken(value="void"),
            CloseParenToken(value=")"),
            OpenBraceToken(value="{"),
            KeywordToken(value="return"),
            ConstantIntegerToken(value="2"),
            SemicolonToken(value=";"),
            CloseBraceToken(value="}"),
        ]

        for ch in program_str:
            target.push_character(ch)
        target.character_stream_done()

        final_tokens = target.completed_token_list
        self.compare_tokens_without_position(expected_tokens, final_tokens)


class TestLexerFailures:
    def test_bad_identifier(self):
        target = Lexer()

        sample_string = "int 123bar;"

        with pytest.raises(LexerError) as le:
            for ch in sample_string:
                target.push_character(ch)
        assert le.value.bad_character == "b"
        assert le.value.position == 7
        assert le.value.previous_tokens == [
            KeywordToken(value="int", start_position=0),
        ]
        assert le.value.message == "No valid action for character"

    def test_bad_character_atsign(self):
        target = Lexer()

        sample_string = "return 0@1;"

        with pytest.raises(LexerError) as le:
            for ch in sample_string:
                target.push_character(ch)
        assert le.value.bad_character == "@"
        assert le.value.position == 8
        assert le.value.previous_tokens == [
            KeywordToken(value="return", start_position=0),
            ConstantIntegerToken(value="0", start_position=7),
        ]
        assert le.value.message == "No token will accept character"

    def test_bad_character_backslash(self):
        target = Lexer()

        sample_string = "\\"

        with pytest.raises(LexerError) as le:
            for ch in sample_string:
                target.push_character(ch)
        assert le.value.bad_character == "\\"
        assert le.value.position == 0
        assert le.value.previous_tokens == []
        assert le.value.message == "No valid token for character"

    def test_bad_character_backtick(self):
        target = Lexer()

        sample_string = "`"

        with pytest.raises(LexerError) as le:
            for ch in sample_string:
                target.push_character(ch)
        assert le.value.bad_character == "`"
        assert le.value.position == 0
        assert le.value.previous_tokens == []
        assert le.value.message == "No valid token for character"


class TestExtractTokens:
    @pytest.mark.parametrize("target", ["int", "void", "return"])
    @pytest.mark.parametrize("idx", [0, 10])
    def test_keywords(self, target: str, idx: int):
        toks = extract_tokens(target, idx)

        assert len(toks) == 2
        assert toks[0] == IdentifierToken(start_position=idx, value=target)
        assert toks[1] == KeywordToken(start_position=idx, value=target)

    @pytest.mark.parametrize("target", ["a", "some_value", "int2", "voida", "return1"])
    @pytest.mark.parametrize("idx", [11, 12])
    def test_identifiers(self, target: str, idx: int):
        toks = extract_tokens(target, idx)

        assert len(toks) == 1
        assert toks[0] == IdentifierToken(start_position=idx, value=target)

    @pytest.mark.parametrize("target", ["000", "010", "100", "1234567890"])
    @pytest.mark.parametrize("idx", [121, 130])
    def test_integers(self, target: str, idx: int):
        toks = extract_tokens(target, idx)

        assert len(toks) == 1
        assert toks[0] == ConstantIntegerToken(start_position=idx, value=target)

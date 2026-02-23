import string

import pytest

from nqcc.lexer import (
    CloseBraceToken,
    CloseParenToken,
    ConstantIntegerToken,
    IdentifierToken,
    KeywordToken,
    Lexer,
    OpenBraceToken,
    OpenParenToken,
    SemicolonToken,
    TokenItem,
    LexerError,
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
            KeywordToken(value="int", position=0),
            ConstantIntegerToken(value="123", position=5),
        ]
        assert le.value.message == "No"

    def test_bad_character_atsign(self):
        target = Lexer()

        sample_string = "return 0@1;"

        for ch in sample_string:
            target.push_character(ch)
        target.character_stream_done()

    def test_bad_character_backslash(self):
        target = Lexer()

        sample_string = "\\"

        for ch in sample_string:
            target.push_character(ch)
        target.character_stream_done()

    def test_bad_character_backtick(self):
        target = Lexer()

        sample_string = "`"

        for ch in sample_string:
            target.push_character(ch)
        target.character_stream_done()

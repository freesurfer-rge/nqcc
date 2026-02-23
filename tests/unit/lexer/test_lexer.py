from nqcc.lexer import (
    CloseParenToken,
    IdentifierToken,
    KeywordToken,
    Lexer,
    OpenParenToken,
)


class TestLexer:
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

class TestLexerFailures:
    def test_bad_identifier(self):
        target = Lexer()

        sample_string = "int 123bar;"

        for ch in sample_string:
            target.push_character(ch)
        target.character_stream_done()

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
import pytest

from nqcc.lexer import (
    AdditionToken,
    CloseBraceToken,
    CloseParenToken,
    ConstantIntegerToken,
    DecrementToken,
    DivideToken,
    IdentifierToken,
    IncrementToken,
    KeywordToken,
    LexerMatchError,
    ModuloToken,
    MultiplyToken,
    NegationToken,
    OpenBraceToken,
    OpenParenToken,
    SemicolonToken,
    TildeToken,
    extract_tokens,
    lex_string,
    pick_token,
)


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

    @pytest.mark.parametrize("idx", [121, 130])
    def test_semicolon(self, idx):
        toks = extract_tokens(";", idx)

        assert len(toks) == 1
        assert toks[0] == SemicolonToken(start_position=idx, value=";")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_open_paren(self, idx):
        toks = extract_tokens("(", idx)

        assert len(toks) == 1
        assert toks[0] == OpenParenToken(start_position=idx, value="(")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_open_brace(self, idx):
        toks = extract_tokens("{", idx)

        assert len(toks) == 1
        assert toks[0] == OpenBraceToken(start_position=idx, value="{")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_close_paren(self, idx):
        toks = extract_tokens(")", idx)

        assert len(toks) == 1
        assert toks[0] == CloseParenToken(start_position=idx, value=")")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_close_brace(self, idx):
        toks = extract_tokens("}", idx)

        assert len(toks) == 1
        assert toks[0] == CloseBraceToken(start_position=idx, value="}")

    @pytest.mark.parametrize("bad_target", ["2int", "\\", "@", "`"])
    def test_bad_strings(self, bad_target: str):
        with pytest.raises(LexerMatchError, match="Lexer failed to match") as lme:
            _ = extract_tokens(bad_target, 10)
        assert lme.value.position == 10

    @pytest.mark.parametrize("idx", [121, 130])
    def test_tilde(self, idx):
        toks = extract_tokens("~", idx)

        assert len(toks) == 1
        assert toks[0] == TildeToken(start_position=idx, value="~")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_negation(self, idx):
        toks = extract_tokens("-", idx)

        assert len(toks) == 1
        assert toks[0] == NegationToken(start_position=idx, value="-")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_decrement(self, idx):
        toks = extract_tokens("--", idx)

        assert len(toks) == 2
        assert toks[0] == DecrementToken(start_position=idx, value="--")
        assert toks[1] == NegationToken(start_position=idx, value="-")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_addition(self, idx):
        toks = extract_tokens("+", idx)

        assert len(toks) == 1
        assert toks[0] == AdditionToken(start_position=idx, value="+")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_increment(self, idx):
        toks = extract_tokens("++", idx)

        assert len(toks) == 2
        assert toks[0] == AdditionToken(start_position=idx, value="+")
        assert toks[1] == IncrementToken(start_position=idx, value="++")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_multiply(self, idx):
        toks = extract_tokens("*", idx)

        assert len(toks) == 1
        assert toks[0] == MultiplyToken(start_position=idx, value="*")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_divide(self, idx):
        toks = extract_tokens("/", idx)

        assert len(toks) == 1
        assert toks[0] == DivideToken(start_position=idx, value="/")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_modulo(self, idx):
        toks = extract_tokens("%", idx)

        assert len(toks) == 1
        assert toks[0] == ModuloToken(start_position=idx, value="%")


class TestPickToken:
    def test_identifier_vs_keyword(self):
        toks = [IdentifierToken(value="int"), KeywordToken(value="int")]

        assert pick_token(toks) == KeywordToken(value="int")

    def test_decrement_vs_negation(self):
        toks = [DecrementToken(value="--"), NegationToken(value="-")]

        assert pick_token(toks) == DecrementToken(value="--")


class TestLexString:
    def test_statement(self):
        sample = "return 2;"

        toks = lex_string(sample)
        assert len(toks) == 3
        assert toks[0] == KeywordToken(start_position=0, value="return")
        assert toks[1] == ConstantIntegerToken(start_position=7, value="2")
        assert toks[2] == SemicolonToken(start_position=8, value=";")

    def test_statement_negation(self):
        sample = "return -2;"

        toks = lex_string(sample)
        assert len(toks) == 4
        assert toks[0] == KeywordToken(start_position=0, value="return")
        assert toks[1] == NegationToken(start_position=7, value="-")
        assert toks[2] == ConstantIntegerToken(start_position=8, value="2")
        assert toks[3] == SemicolonToken(start_position=9, value=";")

    def test_double_tilde(self):
        sample = "return ~~2;"

        toks = lex_string(sample)
        assert len(toks) == 5
        assert toks[0] == KeywordToken(start_position=0, value="return")
        assert toks[1] == TildeToken(start_position=7, value="~")
        assert toks[2] == TildeToken(start_position=8, value="~")
        assert toks[3] == ConstantIntegerToken(start_position=9, value="2")
        assert toks[4] == SemicolonToken(start_position=10, value=";")

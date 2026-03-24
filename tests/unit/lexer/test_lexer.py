import pytest

from nqcc.lexer import (
    AdditionToken,
    BitwiseAnd,
    BitwiseOr,
    BitwiseXor,
    CloseBraceToken,
    CloseParenToken,
    ConstantIntegerToken,
    DecrementToken,
    DivideToken,
    EqualTo,
    IdentifierToken,
    IncrementToken,
    KeywordToken,
    LessThan,
    LessThanOrEqual,
    LexerMatchError,
    LogicalAnd,
    LogicalNot,
    LogicalOr,
    ModuloToken,
    MultiplyToken,
    NegationToken,
    NotEqualTo,
    OpenBraceToken,
    OpenParenToken,
    SemicolonToken,
    TildeToken,
    Token,
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

    @pytest.mark.parametrize("idx", [121, 130])
    def test_bitwiseand(self, idx):
        toks = extract_tokens("&", idx)

        assert len(toks) == 1
        assert toks[0] == BitwiseAnd(start_position=idx, value="&")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_bitwiseor(self, idx):
        toks = extract_tokens("|", idx)

        assert len(toks) == 1
        assert toks[0] == BitwiseOr(start_position=idx, value="|")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_bitwisexor(self, idx):
        toks = extract_tokens("^", idx)

        assert len(toks) == 1
        assert toks[0] == BitwiseXor(start_position=idx, value="^")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_logicalnot(self, idx):
        toks = extract_tokens("!", idx)

        assert len(toks) == 1
        assert toks[0] == LogicalNot(start_position=idx, value="!")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_logicaland(self, idx):
        toks = extract_tokens("&&", idx)

        assert len(toks) == 2
        assert toks[0] == BitwiseAnd(start_position=idx, value="&")
        assert toks[1] == LogicalAnd(start_position=idx, value="&&")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_logicalor(self, idx):
        toks = extract_tokens("||", idx)

        assert len(toks) == 2
        assert toks[0] == BitwiseOr(start_position=idx, value="|")
        assert toks[1] == LogicalOr(start_position=idx, value="||")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_equalto(self, idx):
        toks = extract_tokens("==", idx)

        assert len(toks) == 1
        assert toks[0] == EqualTo(start_position=idx, value="==")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_notequalto(self, idx):
        toks = extract_tokens("!=", idx)

        assert len(toks) == 2
        assert toks[0] == LogicalNot(start_position=idx, value="!")
        assert toks[1] == NotEqualTo(start_position=idx, value="!=")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_lessthan(self, idx):
        toks = extract_tokens("<", idx)

        assert len(toks) == 1
        assert toks[0] == LessThan(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_lessthanorequal(self, idx):
        toks = extract_tokens("<=", idx)

        assert len(toks) == 2
        assert toks[0] == LessThan(start_position=idx)
        assert toks[1] == LessThanOrEqual(start_position=idx)


class TestPickToken:
    def test_identifier_vs_keyword(self):
        toks = [IdentifierToken(value="int"), KeywordToken(value="int")]

        assert pick_token(toks) == KeywordToken(value="int")

    def test_decrement_vs_negation(self):
        toks = [DecrementToken(value="--"), NegationToken(value="-")]

        assert pick_token(toks) == DecrementToken(value="--")

    @pytest.mark.parametrize(
        ["shorter", "longer"],
        [
            (BitwiseAnd(value="&"), LogicalAnd(value="&&")),
            (BitwiseOr(value="|"), LogicalOr(value="||")),
            (LogicalNot(value="!"), NotEqualTo(value="!=")),
            (LessThan(), LessThanOrEqual()),
        ],
    )
    def test_operators_with_substring(self, shorter: Token, longer: Token):
        toks = [shorter, longer]
        assert pick_token(toks) == longer


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

    def test_longer_expression(self):
        sample = "1+2*3/4%2"

        toks = lex_string(sample)
        assert len(toks) == 9
        assert toks[0] == ConstantIntegerToken(start_position=0, value="1")
        assert toks[1] == AdditionToken(start_position=1, value="+")
        assert toks[2] == ConstantIntegerToken(start_position=2, value="2")
        assert toks[3] == MultiplyToken(start_position=3, value="*")
        assert toks[4] == ConstantIntegerToken(start_position=4, value="3")
        assert toks[5] == DivideToken(start_position=5, value="/")
        assert toks[6] == ConstantIntegerToken(start_position=6, value="4")
        assert toks[7] == ModuloToken(start_position=7, value="%")
        assert toks[8] == ConstantIntegerToken(start_position=8, value="2")

    _COMP_MAP = {
        "&&": LogicalAnd,
        "||": LogicalOr,
        "==": EqualTo,
        "!=": NotEqualTo,
        "<": LessThan,
        "<=": LessThanOrEqual,
    }

    @pytest.mark.parametrize("op", ["&&", "||", "==", "!=", "<", ">", "<=", ">="])
    def test_comparison_expression(self, op: str):
        sample = f"1 {op} 3"

        toks = lex_string(sample)
        assert len(toks) == 3
        assert toks[0] == ConstantIntegerToken(start_position=0, value="1")
        assert toks[1] == self._COMP_MAP[op](start_position=2, value=op)
        assert toks[2] == ConstantIntegerToken(start_position=3 + len(op), value="3")

import pytest

from nqcc.lexer import (
    AdditionToken,
    AssignmentToken,
    BitwiseAnd,
    BitwiseOr,
    BitwiseXor,
    CloseBraceToken,
    CloseParenToken,
    ConstantIntegerToken,
    DecrementToken,
    DivideToken,
    EqualTo,
    GreaterThan,
    GreaterThanOrEqual,
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
    extract_tokens,
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

    @pytest.mark.parametrize("idx", [11, 12])
    def test_assignment(self, idx: int):
        target = "="
        toks = extract_tokens(target, idx)

        assert len(toks) == 1
        assert toks[0] == AssignmentToken(start_position=idx)

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
        assert toks[0] == SemicolonToken(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_open_paren(self, idx):
        toks = extract_tokens("(", idx)

        assert len(toks) == 1
        assert toks[0] == OpenParenToken(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_open_brace(self, idx):
        toks = extract_tokens("{", idx)

        assert len(toks) == 1
        assert toks[0] == OpenBraceToken(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_close_paren(self, idx):
        toks = extract_tokens(")", idx)

        assert len(toks) == 1
        assert toks[0] == CloseParenToken(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_close_brace(self, idx):
        toks = extract_tokens("}", idx)

        assert len(toks) == 1
        assert toks[0] == CloseBraceToken(start_position=idx)

    @pytest.mark.parametrize("bad_target", ["2int", "\\", "@", "`"])
    def test_bad_strings(self, bad_target: str):
        with pytest.raises(LexerMatchError, match="Lexer failed to match") as lme:
            _ = extract_tokens(bad_target, 10)
        assert lme.value.position == 10

    @pytest.mark.parametrize("idx", [121, 130])
    def test_tilde(self, idx):
        toks = extract_tokens("~", idx)

        assert len(toks) == 1
        assert toks[0] == TildeToken(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_negation(self, idx):
        toks = extract_tokens("-", idx)

        assert len(toks) == 1
        assert toks[0] == NegationToken(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_decrement(self, idx):
        toks = extract_tokens("--", idx)

        assert len(toks) == 2
        assert toks[0] == DecrementToken(start_position=idx)
        assert toks[1] == NegationToken(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_addition(self, idx):
        toks = extract_tokens("+", idx)

        assert len(toks) == 1
        assert toks[0] == AdditionToken(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_increment(self, idx):
        toks = extract_tokens("++", idx)

        assert len(toks) == 2
        assert toks[0] == AdditionToken(start_position=idx)
        assert toks[1] == IncrementToken(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_multiply(self, idx):
        toks = extract_tokens("*", idx)

        assert len(toks) == 1
        assert toks[0] == MultiplyToken(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_divide(self, idx):
        toks = extract_tokens("/", idx)

        assert len(toks) == 1
        assert toks[0] == DivideToken(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_modulo(self, idx):
        toks = extract_tokens("%", idx)

        assert len(toks) == 1
        assert toks[0] == ModuloToken(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_bitwiseand(self, idx):
        toks = extract_tokens("&", idx)

        assert len(toks) == 1
        assert toks[0] == BitwiseAnd(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_bitwiseor(self, idx):
        toks = extract_tokens("|", idx)

        assert len(toks) == 1
        assert toks[0] == BitwiseOr(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_bitwisexor(self, idx):
        toks = extract_tokens("^", idx)

        assert len(toks) == 1
        assert toks[0] == BitwiseXor(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_logicalnot(self, idx):
        toks = extract_tokens("!", idx)

        assert len(toks) == 1
        assert toks[0] == LogicalNot(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_logicaland(self, idx):
        toks = extract_tokens("&&", idx)

        assert len(toks) == 2
        assert toks[0] == BitwiseAnd(start_position=idx)
        assert toks[1] == LogicalAnd(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_logicalor(self, idx):
        toks = extract_tokens("||", idx)

        assert len(toks) == 2
        assert toks[0] == BitwiseOr(start_position=idx)
        assert toks[1] == LogicalOr(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_equalto(self, idx):
        toks = extract_tokens("==", idx)

        assert len(toks) == 2
        assert toks[0] == AssignmentToken(start_position=idx)
        assert toks[1] == EqualTo(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_notequalto(self, idx):
        toks = extract_tokens("!=", idx)

        assert len(toks) == 2
        assert toks[0] == LogicalNot(start_position=idx)
        assert toks[1] == NotEqualTo(start_position=idx)

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

    @pytest.mark.parametrize("idx", [121, 130])
    def test_greaterthan(self, idx):
        toks = extract_tokens(">", idx)

        assert len(toks) == 1
        assert toks[0] == GreaterThan(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_greaterthanorequal(self, idx):
        toks = extract_tokens(">=", idx)

        assert len(toks) == 2
        assert toks[0] == GreaterThan(start_position=idx)
        assert toks[1] == GreaterThanOrEqual(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_if(self, idx):
        toks = extract_tokens("if", idx)

        assert len(toks) == 2
        assert toks[0] == IdentifierToken(start_position=idx, value="if")
        assert toks[1] == KeywordToken(start_position=idx, value="if")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_else(self, idx):
        toks = extract_tokens("else", idx)

        assert len(toks) == 2
        assert toks[0] == IdentifierToken(start_position=idx, value="else")
        assert toks[1] == KeywordToken(start_position=idx, value="else")

    @pytest.mark.parametrize("idx", [121, 130])
    def test_condquestion(self, idx):
        toks = extract_tokens("?", idx)

        assert len(toks) == 1
        assert toks[0] == GreaterThan(start_position=idx)

    @pytest.mark.parametrize("idx", [121, 130])
    def test_condcolon(self, idx):
        toks = extract_tokens(":", idx)

        assert len(toks) == 1
        assert toks[0] == GreaterThan(start_position=idx)

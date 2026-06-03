import pytest

from nqcc.lexer import (
    AdditionToken,
    AssignmentToken,
    BitwiseAnd,
    BitwiseOr,
    ConstantIntegerToken,
    DecrementToken,
    DivideToken,
    EqualTo,
    GreaterThan,
    GreaterThanOrEqual,
    IdentifierToken,
    KeywordToken,
    LessThan,
    LessThanOrEqual,
    LogicalAnd,
    LogicalNot,
    LogicalOr,
    ModuloToken,
    MultiplyToken,
    NegationToken,
    NotEqualTo,
    SemicolonToken,
    TildeToken,
    Token,
    lex_string,
    pick_token,
)


class TestPickToken:
    @pytest.mark.parametrize(
        "value",
        {
            "int",
            "return",
            "void",
            "if",
            "else",
            "do",
            "while",
            "for",
            "break",
            "continue",
            "extern",
            "static",
        },
    )
    def test_identifier_vs_keyword(self, value: str):
        toks = [IdentifierToken(value=value), KeywordToken(value=value)]

        assert pick_token(toks) == KeywordToken(value=value)

    def test_decrement_vs_negation(self):
        toks = [DecrementToken(), NegationToken()]

        assert pick_token(toks) == DecrementToken()

    @pytest.mark.parametrize(
        ["shorter", "longer"],
        [
            (BitwiseAnd(), LogicalAnd()),
            (BitwiseOr(), LogicalOr()),
            (LogicalNot(), NotEqualTo()),
            (LessThan(), LessThanOrEqual()),
            (GreaterThan(), GreaterThanOrEqual()),
            (AssignmentToken(), EqualTo()),
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
        ">": GreaterThan,
        ">=": GreaterThanOrEqual,
    }

    @pytest.mark.parametrize("op", ["&&", "||", "==", "!=", "<", ">", "<=", ">="])
    def test_comparison_expression(self, op: str):
        sample = f"1 {op} 3"

        toks = lex_string(sample)
        assert len(toks) == 3
        assert toks[0] == ConstantIntegerToken(start_position=0, value="1")
        assert toks[1] == self._COMP_MAP[op](start_position=2)
        assert toks[2] == ConstantIntegerToken(start_position=3 + len(op), value="3")

    def test_assignment(self):
        sample = "a = 2"

        toks = lex_string(sample)
        assert len(toks) == 3
        assert toks[0] == IdentifierToken(start_position=0, value="a")
        assert toks[1] == AssignmentToken(start_position=2)
        assert toks[2] == ConstantIntegerToken(start_position=4, value="2")

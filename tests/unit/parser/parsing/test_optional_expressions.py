import pytest

from nqcc.lexer import SemicolonToken, CloseParenToken
from nqcc.parser import (
    SourceAdd,
    SourceAssignmentNode,
    SourceBinaryExpressionNode,
    SourceBitwiseAnd,
    SourceBitwiseOr,
    SourceBitwiseXor,
    SourceComplement,
    SourceConstantIntNode,
    SourceDivide,
    SourceEqualTo,
    SourceGreaterThan,
    SourceGreaterThanOrEqual,
    SourceLeftShift,
    SourceLessThan,
    SourceLessThanOrEqual,
    SourceLogicalAnd,
    SourceLogicalNot,
    SourceLogicalOr,
    SourceModulo,
    SourceMultiply,
    SourceNegate,
    SourceNotEqualTo,
    SourceRightShift,
    SourceSubtract,
    SourceTernaryExpressonNode,
    SourceUnaryExpressionNode,SourceDeclarationNode,
    SourceVarNode,
    TokenTape,
    parse_optional_expression,
)

class TestOptionalForInit:
    def test_missing(self):
        source = ";"
        token_tape = TokenTape.from_c_source(source)
        result = parse_optional_expression(token_tape, SemicolonToken)
        assert result is None
        assert token_tape.tokens_remaining == 0

    def test_init(self):
        source = "i=20;"
        token_tape = TokenTape.from_c_source(source)
        result = parse_optional_expression(token_tape, SemicolonToken)
        assert isinstance(result, SourceAssignmentNode)
        assert result.left == SourceVarNode(start_position=0, identifier="i")
        assert result.right == SourceConstantIntNode(start_position=2, value=20)
        assert token_tape.tokens_remaining == 0

    def test_decl(self):
        source = " int a = 32;"
        token_tape = TokenTape.from_c_source(source)
        result = parse_optional_expression(token_tape, SemicolonToken)
        assert isinstance(result, SourceDeclarationNode)
        assert result.identifier == SourceVarNode(start_position=5, identifier="a")
        assert result.initial == SourceConstantIntNode(start_position=9, value=32)
        assert token_tape.tokens_remaining == 0

class TestOptionalForPost:
    def test_missing(self):
        source = ")"
        token_tape = TokenTape.from_c_source(source)
        result = parse_optional_expression(token_tape, CloseParenToken)
        assert result is None
        assert token_tape.tokens_remaining == 0

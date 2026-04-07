import pytest

from nqcc.lexer import ConstantIntegerToken, KeywordToken, SemicolonToken
from nqcc.parser import (
    SourceAdd,
    SourceAssignmentNode,
    SourceASTBadValueError,
    SourceBinaryExpressionNode,
    SourceConstantIntNode,
    SourceExpressionStatementNode,
    SourceGreaterThan,
    SourceIfStatementNode,
    SourceMultiply,
    SourceNullStatementNode,
    SourceReturnNode,
    SourceVarNode,
    TokenTape,
    parse_statement,
)


class TestSourceStatementNode:
    def test_return_statement(self):
        tokens = [
            KeywordToken(start_position=0, value="return"),
            ConstantIntegerToken(start_position=1, value="321"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        node = parse_statement(token_tape)

        assert isinstance(node, SourceReturnNode)
        assert node.start_position == 0
        assert isinstance(node.value, SourceConstantIntNode)
        assert node.value.start_position == 1
        assert node.value.value == 321

        assert token_tape.tokens_remaining == 0

    def test_return_mispelled(self):
        tokens = [
            KeywordToken(start_position=0, value="returns"),
            ConstantIntegerToken(start_position=1, value="321"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        with pytest.raises(SourceASTBadValueError) as sabve:
            _ = parse_statement(token_tape)
        assert sabve.value.message == "Unexpected keyword"
        assert sabve.value.actual_token == tokens[0]

    def test_return_has_space(self):
        tokens = [
            KeywordToken(start_position=0, value="retur n"),
            ConstantIntegerToken(start_position=1, value="321"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        with pytest.raises(SourceASTBadValueError) as sabve:
            _ = parse_statement(token_tape)
        assert sabve.value.message == "Unexpected keyword"
        assert sabve.value.actual_token == tokens[0]

    def test_null_statement(self):
        c_str = ";"
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 1

        node = parse_statement(token_tape)
        assert isinstance(node, SourceNullStatementNode)
        assert node.start_position == 0
        assert token_tape.tokens_remaining == 0

    def test_complex_statement(self):
        c_str = "a = 3 * (b = a);"
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 10

        node = parse_statement(token_tape)
        assert isinstance(node, SourceExpressionStatementNode)
        assert token_tape.tokens_remaining == 0
        assert isinstance(node.value, SourceAssignmentNode)
        assert node.value.left == SourceVarNode(start_position=0, identifier="a")
        assert isinstance(node.value.right, SourceBinaryExpressionNode)
        mul_exp = node.value.right
        assert mul_exp.operator == SourceMultiply(start_position=6)
        assert mul_exp.left == SourceConstantIntNode(start_position=4, value=3)
        assert isinstance(mul_exp.right, SourceAssignmentNode)
        mul_assign = mul_exp.right
        assert mul_assign.left == SourceVarNode(start_position=9, identifier="b")
        assert mul_assign.right == SourceVarNode(start_position=13, identifier="a")
        assert token_tape.tokens_remaining == 0

    def test_return_addition(self):
        c_str = "return a + b;"
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 5

        node = parse_statement(token_tape)
        assert isinstance(node, SourceReturnNode)
        assert isinstance(node.value, SourceBinaryExpressionNode)
        assert node.value.operator == SourceAdd(start_position=9)
        assert node.value.left == SourceVarNode(start_position=7, identifier="a")
        assert node.value.right == SourceVarNode(start_position=11, identifier="b")
        assert token_tape.tokens_remaining == 0


class TestSourceIfStatementNode:
    def test_simple(self):
        # Have extra semicolon to ensure we don't run out of tokens
        c_str = "if( a ) b=1; ;"
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 9

        node = parse_statement(token_tape)
        assert isinstance(node, SourceIfStatementNode)
        assert node.start_position == 0

        assert isinstance(node.condition, SourceVarNode)
        assert node.condition.identifier == "a"

        assert isinstance(node.then, SourceExpressionStatementNode)
        assert isinstance(node.then.value, SourceAssignmentNode)
        assert isinstance(node.then.value.left, SourceVarNode)
        assert node.then.value.left.identifier == "b"
        assert isinstance(node.then.value.right, SourceConstantIntNode)
        assert node.then.value.right.value == 1

        assert node.otherwise is None

        # Should not have touched the extra semicolon
        assert token_tape.tokens_remaining == 1

    def test_with_else(self):
        c_str = "if( a ) b=1; else c=2;"
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 13

        node = parse_statement(token_tape)
        assert isinstance(node, SourceIfStatementNode)
        assert node.start_position == 0

        assert isinstance(node.condition, SourceVarNode)
        assert node.condition.identifier == "a"

        assert isinstance(node.then, SourceExpressionStatementNode)
        assert isinstance(node.then.value, SourceAssignmentNode)
        assert isinstance(node.then.value.left, SourceVarNode)
        assert node.then.value.left.identifier == "b"
        assert isinstance(node.then.value.right, SourceConstantIntNode)
        assert node.then.value.right.value == 1

        assert isinstance(node.otherwise, SourceExpressionStatementNode)
        assert isinstance(node.otherwise.value, SourceAssignmentNode)
        assert isinstance(node.otherwise.value.left, SourceVarNode)
        assert node.otherwise.value.left.identifier == "c"
        assert isinstance(node.otherwise.value.right, SourceConstantIntNode)
        assert node.otherwise.value.right.value == 2

        # Should have consumed everything
        assert token_tape.tokens_remaining == 0

    def test_nested(self):
        # Again, tag an extra semicolon onto the end
        c_str = """if (a)
        if( a>10 )
           return a;
        else
           return b;

        ;
"""
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 18

        node = parse_statement(token_tape)
        assert isinstance(node, SourceIfStatementNode)
        assert node.start_position == 0

        assert isinstance(node.condition, SourceVarNode)
        assert node.condition.identifier == "a"

        assert isinstance(node.then, SourceIfStatementNode)
        assert node.otherwise is None
        inner = node.then
        assert isinstance(inner.condition, SourceBinaryExpressionNode)
        assert isinstance(inner.condition.operator, SourceGreaterThan)
        assert isinstance(inner.condition.left, SourceVarNode)
        assert inner.condition.left.identifier == "a"
        assert isinstance(inner.condition.right, SourceConstantIntNode)
        assert inner.condition.right.value == 10

        assert isinstance(inner.then, SourceReturnNode)
        assert isinstance(inner.then.value, SourceVarNode)
        assert inner.then.value.identifier == "a"
        assert isinstance(inner.otherwise, SourceReturnNode)
        assert isinstance(inner.otherwise.value, SourceVarNode)
        assert inner.otherwise.value.identifier == "b"

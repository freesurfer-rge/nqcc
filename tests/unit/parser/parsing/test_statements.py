import pytest

from nqcc.lexer import ConstantIntegerToken, KeywordToken, SemicolonToken
from nqcc.parser import (
    SourceAdd,
    SourceAssignmentNode,
    SourceASTBadValueError,
    SourceBinaryExpressionNode,
    SourceConstantIntNode,
    SourceExpressionStatementNode,
    SourceMultiply,
    SourceNullStatementNode,
    SourceReturnNode,
    SourceVarNode,
    TokenTape,SourceIfStatementNode,
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
        c_str = "if( a ) b=1;"
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 8

        node = parse_statement(token_tape)
        assert isinstance(node, SourceIfStatementNode)
        assert node.start_position == 0

        assert isinstance(node.condition, SourceVarNode)
        assert node.condition.identifier == "a"

        assert isinstance(node.then, SourceAssignmentNode)
        assert isinstance(node.then.left, SourceVarNode)
        assert node.then.left.identifier == "b"
        assert isinstance(node.then.right, SourceConstantIntNode)
        assert node.then.right.value == 1

        assert token_tape.tokens_remaining == 0
import pytest

from nqcc.lexer import ConstantIntegerToken, KeywordToken, SemicolonToken
from nqcc.parser import (
    SourceASTBadValueError,
    SourceConstantIntNode,
    SourceReturnNode,
    SourceBinaryExpressionNode,
    SourceAdd,
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

    def test_complex_statement(self):
        c_str = "a = 3 * (b = a);"
        token_tape = TokenTape.from_c_source(c_str)
        assert token_tape.tokens_remaining == 10

        node = parse_statement(token_tape)

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

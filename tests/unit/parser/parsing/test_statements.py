import pytest

from nqcc.lexer import ConstantIntegerToken, KeywordToken, SemicolonToken
from nqcc.parser import (
    SourceASTBadValueError,
    SourceConstantIntNode,
    SourceReturnNode,
    SourceStatementNode,
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

    def test_return_serde(self):
        tokens = [
            KeywordToken(start_position=0, value="return"),
            ConstantIntegerToken(start_position=1, value="321"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        node = parse_statement(token_tape)

        node_str = node.model_dump_json()

        node_serde = SourceStatementNode.model_validate_json(node_str)

        assert node == node_serde

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

import json

from nqcc.lexer import ConstantIntegerToken, KeywordToken, SemicolonToken
from nqcc.parser import (
    SourceConstantIntNode,
    SourceExpressionNode,
    SourceFunctionNode,
    SourceReturnNode,
    SourceStatementNode,
    TokenTape,
    parse_expression,
    parse_statement,
    parse_function,
)


class TestSourceExpressionNode:
    def test_constant_integer(self):
        tokens = [
            ConstantIntegerToken(start_position=1, value="123"),
            SemicolonToken(start_position=5, value=";"),
        ]
        token_tape = TokenTape(tokens)

        node = parse_expression(token_tape)
        assert isinstance(node, SourceConstantIntNode)
        assert node.start_position == 1
        assert node.value == 123

        # The expression doesn't consume the semicolon
        assert token_tape.tokens_remaining == 1


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
        sen: SourceConstantIntNode = node.value
        assert sen.start_position == 1
        assert sen.value == 321

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


class TestSourceFunctionDefinitionNode:
    def test_function(self):
        program_str = "int main( void ) { return 2;}"

        token_tape = TokenTape.from_c_source(program_str)

        node = parse_function(token_tape)

        assert isinstance(node, SourceFunctionNode)
        assert node.start_position == program_str.find("int")
        assert node.identifier == "main"

        body_node = node.body
        assert isinstance(body_node, SourceReturnNode)
        assert body_node.start_position == program_str.find("return")

        return_value_node = body_node.value
        assert isinstance(return_value_node, SourceConstantIntNode)
        assert return_value_node.start_position == program_str.find("2")

    def test_serde(self):
        program_str = "int main( void ) { return 2;}"

        token_tape = TokenTape.from_c_source(program_str)

        node = parse_function(token_tape)

        node_str = node.model_dump_json()

        # This is slightly ugly, but we need to make sure we can deserialise
        # all possibilities
        node_serde = SourceFunctionNode.model_validate_json(node_str)

        assert node == node_serde

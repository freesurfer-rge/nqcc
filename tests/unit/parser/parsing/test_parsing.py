import pytest

from nqcc.lexer import CloseParenToken
from nqcc.parser import (
    SourceASTBadTypeError,
    SourceConstantIntNode,
    SourceFunctionNode,
    SourceProgramNode,
    SourceReturnNode,
    TokenTape,
    parse_function,
    parse_program,
)


class TestSourceFunctionNode:
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

        node_serde = SourceFunctionNode.model_validate_json(node_str)
        assert node == node_serde

    def test_switched_parens(self):
        program_str = "int main) void ( { return 2;}"

        token_tape = TokenTape.from_c_source(program_str)

        with pytest.raises(SourceASTBadTypeError) as sabte:
            _ = parse_function(token_tape)
        assert sabte.value.message == "Received token of unexpected type"
        assert sabte.value.actual_token == CloseParenToken(start_position=8, value=")")

    def test_missing_close_brace(self):
        program_str = "int main( void ) { return 2;"
        token_tape = TokenTape.from_c_source(program_str)

        with pytest.raises(IndexError, match="No tokens remaining in TokenTape"):
            _ = parse_function(token_tape)


class TestSourceProgramNode:
    def test_program(self):
        program_str = " int main( void ) { return 2;}"

        token_tape = TokenTape.from_c_source(program_str)

        node = parse_program(token_tape)

        assert isinstance(node, SourceProgramNode)
        assert node.start_position == 0

        func_node = node.value
        assert isinstance(func_node, SourceFunctionNode)

        assert func_node.identifier == "main"

        body_node = func_node.body
        assert isinstance(body_node, SourceReturnNode)
        assert body_node.start_position == program_str.find("return")

        return_value_node = body_node.value
        assert isinstance(return_value_node, SourceConstantIntNode)
        assert return_value_node.start_position == program_str.find("2")

    def test_program_serde(self):
        program_str = "   int main( void ) { return 6;}"

        token_tape = TokenTape.from_c_source(program_str)

        node = parse_program(token_tape)
        node_str = node.model_dump_json()

        node_serde = SourceProgramNode.model_validate_json(node_str)
        assert node == node_serde

import pytest

from nqcc.lexer import CloseParenToken
from nqcc.parser import (
    SourceAdd,
    SourceASTBadTypeError,
    SourceBinaryExpressionNode,
    SourceConstantIntNode,
    SourceDeclarationNode,
    SourceFunctionNode,
    SourceProgramNode,
    SourceReturnNode,
    SourceVarNode,
    TokenTape,
    parse_declaration,
    parse_function,
    parse_program,
)


class TestSourceDeclarationNode:
    def test_no_initial(self):
        cdecl_str = "int a;"
        token_tape = TokenTape.from_c_source(cdecl_str)

        node = parse_declaration(token_tape)
        assert token_tape.tokens_remaining == 0

        assert isinstance(node, SourceDeclarationNode)
        assert node.start_position == 0
        assert node.identifier == SourceVarNode(start_position=4, identifier="a")
        assert not node.initial

    def test_constant_initial(self):
        cdecl_str = "int a=1;"
        token_tape = TokenTape.from_c_source(cdecl_str)

        node = parse_declaration(token_tape)
        assert token_tape.tokens_remaining == 0

        assert isinstance(node, SourceDeclarationNode)
        assert node.start_position == 0
        assert node.identifier == SourceVarNode(start_position=4, identifier="a")
        assert node.initial == SourceConstantIntNode(start_position=6, value=1)

    def test_expressions_initial(self):
        cdecl_str = "int a=1+2;"
        token_tape = TokenTape.from_c_source(cdecl_str)

        node = parse_declaration(token_tape)
        assert token_tape.tokens_remaining == 0

        assert isinstance(node, SourceDeclarationNode)
        assert node.start_position == 0
        assert node.identifier == SourceVarNode(start_position=4, identifier="a")
        assert node.initial == SourceBinaryExpressionNode(
            start_position=7,
            operator=SourceAdd(start_position=7),
            left=SourceConstantIntNode(start_position=6, value=1),
            right=SourceConstantIntNode(start_position=8, value=2),
        )


class TestSourceFunctionNode:
    def test_function_simple(self):
        program_str = "int main( void ) { return 2;}"

        token_tape = TokenTape.from_c_source(program_str)

        node = parse_function(token_tape)

        assert isinstance(node, SourceFunctionNode)
        assert node.start_position == program_str.find("int")
        assert node.identifier == "main"

        assert isinstance(node.body, list)
        assert len(node.body) == 1
        assert isinstance(node.body[0], SourceReturnNode)
        assert node.body[0].start_position == program_str.find("return")

        return_value_node = node.body[0].value
        assert isinstance(return_value_node, SourceConstantIntNode)
        assert return_value_node.start_position == program_str.find("2")

    def test_function_two_statement(self):
        program_str = "int main(void){int a=11; return a;}"
        token_tape = TokenTape.from_c_source(program_str)

        node = parse_function(token_tape)

        assert isinstance(node, SourceFunctionNode)
        assert node.start_position == program_str.find("int")
        assert node.identifier == "main"

        assert isinstance(node.body, list)
        assert len(node.body) == 2
        assert node.body[0] == SourceDeclarationNode(
            start_position=15,
            identifier=SourceVarNode(start_position=19, identifier="a"),
            initial=SourceConstantIntNode(start_position=21, value=11),
        )
        assert node.body[1] == SourceReturnNode(
            start_position=25, value=SourceVarNode(start_position=32, identifier="a")
        )

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

        assert isinstance(func_node.body, list)
        assert len(func_node.body) == 1
        assert isinstance(func_node.body[0], SourceReturnNode)
        assert func_node.body[0].start_position == program_str.find("return")

        return_value_node = func_node.body[0].value
        assert isinstance(return_value_node, SourceConstantIntNode)
        assert return_value_node.start_position == program_str.find("2")

    def test_program_serde(self):
        program_str = "   int main( void ) { return 6;}"

        token_tape = TokenTape.from_c_source(program_str)

        node = parse_program(token_tape)
        node_str = node.model_dump_json()

        node_serde = SourceProgramNode.model_validate_json(node_str)
        assert node == node_serde

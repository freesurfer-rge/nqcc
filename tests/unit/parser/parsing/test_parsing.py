import pytest

from nqcc.lexer import CloseParenToken
from nqcc.parser import (
    SourceAdd,
    SourceASTBadTypeError,
    SourceBinaryExpressionNode,
    SourceBlockNode,
    SourceConstantIntNode,
    SourceFunctionDeclarationNode,
    SourceProgramNode,
    SourceReturnNode,
    SourceVariableDeclarationNode,
    SourceVarNode,
    TokenTape,
    parse_declaration,
    parse_function,
    parse_function_parameter_list,
    parse_program,
)


class TestParseFunctionParameterList:
    def test_void(self):
        param_str = "(void)"
        token_tape = TokenTape.from_c_source(param_str)

        params = parse_function_parameter_list(token_tape)
        assert isinstance(params, list)
        assert len(params) == 0

    def test_single(self):
        param_str = " ( int a    ) "
        token_tape = TokenTape.from_c_source(param_str)

        params = parse_function_parameter_list(token_tape)
        assert isinstance(params, list)
        assert len(params) == 1
        assert params[0] == "a"

    def test_two_params(self):
        param_str = " ( int a, int b_parameter   ) "
        token_tape = TokenTape.from_c_source(param_str)

        params = parse_function_parameter_list(token_tape)
        assert isinstance(params, list)
        assert len(params) == 2
        assert params[0] == "a"
        assert params[1] == "b_parameter"


class TestSourceVariableDeclarationNode:
    def test_no_initial(self):
        cdecl_str = "int a;"
        token_tape = TokenTape.from_c_source(cdecl_str)

        node = parse_declaration(token_tape)
        assert token_tape.tokens_remaining == 0

        assert isinstance(node, SourceVariableDeclarationNode)
        assert node.start_position == 0
        assert node.identifier == SourceVarNode(start_position=4, identifier="a")
        assert not node.initial

    def test_constant_initial(self):
        cdecl_str = "int a=1;"
        token_tape = TokenTape.from_c_source(cdecl_str)

        node = parse_declaration(token_tape)
        assert token_tape.tokens_remaining == 0

        assert isinstance(node, SourceVariableDeclarationNode)
        assert node.start_position == 0
        assert node.identifier == SourceVarNode(start_position=4, identifier="a")
        assert node.initial == SourceConstantIntNode(start_position=6, value=1)

    def test_expressions_initial(self):
        cdecl_str = "int a=1+2;"
        token_tape = TokenTape.from_c_source(cdecl_str)

        node = parse_declaration(token_tape)
        assert token_tape.tokens_remaining == 0

        assert isinstance(node, SourceVariableDeclarationNode)
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

        assert isinstance(node, SourceFunctionDeclarationNode)
        assert node.start_position == program_str.find("int")
        assert node.identifier == "main"

        assert isinstance(node.body, SourceBlockNode)
        assert len(node.body.items) == 1
        assert isinstance(node.body.items[0], SourceReturnNode)
        assert node.body.items[0].start_position == program_str.find("return")

        return_value_node = node.body.items[0].value
        assert isinstance(return_value_node, SourceConstantIntNode)
        assert return_value_node.start_position == program_str.find("2")

    def test_function_two_statement(self):
        program_str = "int main(void){int a=11; return a;}"
        token_tape = TokenTape.from_c_source(program_str)

        node = parse_function(token_tape)

        assert isinstance(node, SourceFunctionDeclarationNode)
        assert node.start_position == program_str.find("int")
        assert node.identifier == "main"

        assert isinstance(node.body, SourceBlockNode)
        assert len(node.body.items) == 2
        assert node.body.items[0] == SourceVariableDeclarationNode(
            start_position=15,
            identifier=SourceVarNode(start_position=19, identifier="a"),
            initial=SourceConstantIntNode(start_position=21, value=11),
        )
        assert node.body.items[1] == SourceReturnNode(
            start_position=25, value=SourceVarNode(start_position=32, identifier="a")
        )

    def test_serde(self):
        program_str = "int main( void ) { return 2;}"

        token_tape = TokenTape.from_c_source(program_str)

        node = parse_function(token_tape)

        node_str = node.model_dump_json()

        node_serde = SourceFunctionDeclarationNode.model_validate_json(node_str)
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

        assert len(node.functions) == 1
        func_node = node.functions[0]
        assert isinstance(func_node, SourceFunctionDeclarationNode)

        assert func_node.identifier == "main"

        assert isinstance(func_node.body, SourceBlockNode)
        assert len(func_node.body.items) == 1
        assert isinstance(func_node.body.items[0], SourceReturnNode)
        assert func_node.body.items[0].start_position == program_str.find("return")

        return_value_node = func_node.body.items[0].value
        assert isinstance(return_value_node, SourceConstantIntNode)
        assert return_value_node.start_position == program_str.find("2")

    def test_program_serde(self):
        program_str = "   int main( void ) { return 6;}"

        token_tape = TokenTape.from_c_source(program_str)

        node = parse_program(token_tape)
        node_str = node.model_dump_json()

        node_serde = SourceProgramNode.model_validate_json(node_str)
        assert node == node_serde

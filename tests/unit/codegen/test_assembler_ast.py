from nqcc.codegen import (
    AsmFunctionNode,
    AsmImmediateIntNode,
    AsmMovNode,
    AsmProgramNode,
    AsmRegisterNode,
    AsmRetNode,
    convert_expression_node,
    convert_function_node,
    convert_program_node,
    convert_statement_node,
)
from nqcc.parser import (
    SourceConstantIntNode,
    SourceReturnNode,
    TokenTape,
    parse_function,
    parse_program,
)


class TestConvertExpressions:
    def test_smoke(self):
        source_node = SourceConstantIntNode(start_position=0, value=123)

        result = convert_expression_node(source_node)
        assert isinstance(result, AsmImmediateIntNode)
        assert result.start_position == 0
        assert result.value == 123


class TestConvertStatementNode:
    def test_smoke(self):
        source_node = SourceReturnNode(
            start_position=0, value=SourceConstantIntNode(start_position=2, value=312)
        )

        result = convert_statement_node(source_node)
        assert isinstance(result, list)
        assert len(result) == 2

        instr0 = result[0]
        assert isinstance(instr0, AsmMovNode)
        assert instr0.start_position == 0
        assert isinstance(instr0.source, AsmImmediateIntNode)
        assert instr0.source.start_position == 2
        assert instr0.source.value == 312
        assert isinstance(instr0.destination, AsmRegisterNode)
        assert instr0.destination.start_position == 2
        assert instr0.destination.value == "eax"

        instr1 = result[1]
        assert isinstance(instr1, AsmRetNode)
        assert instr1.start_position == 0


class TestConvertFunctionNode:
    def test_smoke(self):
        program_str = "int main( void ) { return 45;}"

        token_tape = TokenTape.from_c_source(program_str)

        node = parse_function(token_tape)

        result = convert_function_node(node)

        assert isinstance(result, AsmFunctionNode)
        assert result.identifier == "main"
        assert result.start_position == 0
        assert len(result.instructions) == 2

        instr0 = result.instructions[0]
        assert isinstance(instr0, AsmMovNode)
        assert instr0.start_position == 19
        assert instr0.source == AsmImmediateIntNode(start_position=26, value=45)
        assert instr0.destination == AsmRegisterNode(start_position=26, value="eax")

        assert result.instructions[1] == AsmRetNode(start_position=19)


class TestConvertProgramNode:
    def test_smoke(self):
        program_str = "   int main( void ) { return 46;}"

        token_tape = TokenTape.from_c_source(program_str)

        node = parse_program(token_tape)

        result = convert_program_node(node)

        assert isinstance(result, AsmProgramNode)
        assert result.start_position == 0

        func_node = result.value
        assert isinstance(func_node, AsmFunctionNode)
        assert func_node.identifier == "main"
        assert func_node.start_position == 3
        assert len(func_node.instructions) == 2

        instr0 = func_node.instructions[0]
        assert isinstance(instr0, AsmMovNode)
        assert instr0.start_position == 22
        assert instr0.source == AsmImmediateIntNode(start_position=29, value=46)
        assert instr0.destination == AsmRegisterNode(start_position=29, value="eax")

        assert func_node.instructions[1] == AsmRetNode(start_position=22)

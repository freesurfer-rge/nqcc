from nqcc.codegen import (
    AsmImmediateIntNode,
    AsmMovNode,
    AsmRegisterNode,
    AsmRetNode,
    AsmFunctionNode,
    convert_expression_node,
    convert_statement_node,
    convert_function_node,
)
from nqcc.parser import SourceConstantIntNode, SourceReturnNode, TokenTape, parse_function


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
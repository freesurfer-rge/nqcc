from nqcc.codegen import (
    AsmImmediateIntNode,
    AsmMovNode,
    AsmRegisterNode,
    AsmRetNode,
    convert_expression_node,
    convert_statement_node,
)
from nqcc.parser import SourceConstantIntNode, SourceReturnNode


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

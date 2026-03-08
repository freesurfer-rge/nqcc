import pytest

from nqcc.codegen import (
    AsmImmediateIntNode,
    AsmOperandNode,
    AsmPseudoRegisterNode,
    AsmRegisterNode,
    AsmStackNode,
    PseudoRegisterReplacer,
)


class TestPseudoRegisterReplacer:
    @pytest.mark.parametrize(
        "operand",
        [
            AsmImmediateIntNode(start_position=12, value=2),
            AsmRegisterNode(start_position=3, value="eax"),
            AsmStackNode(start_position=32, offset=-4),
        ],
    )
    def test_unchanged_operands(self, operand: AsmOperandNode):
        orig_op = operand.model_copy(deep=True)
        target = PseudoRegisterReplacer()

        result = target.get_updated_operand(orig_op)
        assert result == orig_op

    def test_single_operand(self):
        pseudo_op = AsmPseudoRegisterNode(start_position=312, identifier="temp.0")
        target = PseudoRegisterReplacer()

        result0 = target.get_updated_operand(pseudo_op)
        assert isinstance(result0, AsmStackNode)
        assert result0.start_position == 312
        assert result0.offset == -4

        result1 = target.get_updated_operand(pseudo_op)
        assert result1 == result0

    def test_two_operands(self):
        pseudo_op0 = AsmPseudoRegisterNode(start_position=312, identifier="temp.0")
        pseudo_op1 = AsmPseudoRegisterNode(start_position=312, identifier="temp.1")
        target = PseudoRegisterReplacer()

        result0 = target.get_updated_operand(pseudo_op0)
        assert isinstance(result0, AsmStackNode)
        assert result0.start_position == 312
        assert result0.offset == -4

        result1 = target.get_updated_operand(pseudo_op1)
        assert isinstance(result0, AsmStackNode)
        assert result1.start_position == 312
        assert result1.offset == -8

        result2 = target.get_updated_operand(pseudo_op0)
        assert result2 == result0

        result3 = target.get_updated_operand(pseudo_op1)
        assert result3 == result1

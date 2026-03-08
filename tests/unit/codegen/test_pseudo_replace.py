import pytest

from nqcc.codegen import (
    AsmAllocateStackNode,
    AsmImmediateIntNode,
    AsmInstructionNode,
    AsmMovNode,
    AsmNegOperator,
    AsmNotOperator,
    AsmOperandNode,
    AsmPseudoRegisterNode,
    AsmRegisterNode,
    AsmRetNode,
    AsmStackNode,
    AsmUnaryNode,
    AsmUnaryOperator,
    PseudoRegisterReplacer,
)


class TestOperandUpdate:
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


class TestInstructionUpdate:
    @pytest.mark.parametrize(
        "instr",
        [AsmRetNode(start_position=25), AsmAllocateStackNode(start_position=99, stack_size=126)],
    )
    def test_unchanged_instructions(self, instr: AsmInstructionNode):
        orig_instr = instr.model_copy(deep=True)
        target = PseudoRegisterReplacer()
        target.update_instruction(instr)
        assert orig_instr == instr

    def test_mov(self):
        target = PseudoRegisterReplacer()

        pseudo_op0 = AsmPseudoRegisterNode(start_position=312, identifier="temp.0")
        pseudo_op1 = AsmPseudoRegisterNode(start_position=313, identifier="temp.1")

        mov_node = AsmMovNode(start_position=31, source=pseudo_op0, destination=pseudo_op1)

        target.update_instruction(mov_node)
        assert mov_node.start_position == 31
        assert mov_node.source == AsmStackNode(start_position=312, offset=-4)
        assert mov_node.destination == AsmStackNode(start_position=313, offset=-8)

    @pytest.mark.parametrize(
        "op", [AsmNotOperator(start_position=13), AsmNegOperator(start_position=14)]
    )
    def test_unary(self, op: AsmUnaryOperator):
        target = PseudoRegisterReplacer()

        pseudo_op0 = AsmPseudoRegisterNode(start_position=315, identifier="temp.0")
        unary_node = AsmUnaryNode(start_position=32, operator=op, source=pseudo_op0)

        target.update_instruction(unary_node)
        assert unary_node.start_position == 32
        assert unary_node.operator == op
        assert unary_node.source == AsmStackNode(start_position=315, offset=-4)


class TestFunctionUpdate:
    def test_tbd(self):
        raise NotImplementedError("well...")

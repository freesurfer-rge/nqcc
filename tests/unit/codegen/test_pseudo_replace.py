import pytest

from nqcc.codegen import (
    AsmAdd,
    AsmAllocateStackNode,
    AsmBinaryNode,
    AsmBinaryOperator,
    AsmCdqNode,
    AsmIDivNode,
    AsmImmediateIntNode,
    AsmInstructionNode,
    AsmMovNode,
    AsmMultiply,
    AsmNeg,
    AsmNot,
    AsmOperandNode,
    AsmPseudoRegisterNode,
    AsmRegisterNode,
    AsmRetNode,
    AsmStackNode,
    AsmSubtract,
    AsmUnaryNode,
    AsmUnaryOperator,
    PseudoRegisterReplacer,
    convert_tacky_function,
    convert_tacky_program,
)
from nqcc.parser import TokenTape, parse_function, parse_program
from nqcc.tacky import TackyGenerator


class TestOperandUpdate:
    @pytest.mark.parametrize(
        "operand",
        [
            AsmImmediateIntNode(start_position=12, value=2),
            AsmRegisterNode(start_position=3, value="AX"),
            AsmStackNode(start_position=32, offset=-4),
        ],
    )
    def test_unchanged_operands(self, operand: AsmOperandNode):
        orig_op = operand.model_copy(deep=True)
        target = PseudoRegisterReplacer()

        result = target.get_updated_operand(orig_op)
        assert result == orig_op
        assert target.curr_offset == 0

    def test_single_operand(self):
        pseudo_op = AsmPseudoRegisterNode(start_position=312, identifier="temp.0")
        target = PseudoRegisterReplacer()

        result0 = target.get_updated_operand(pseudo_op)
        assert isinstance(result0, AsmStackNode)
        assert result0.start_position == 312
        assert result0.offset == -4
        assert target.curr_offset == -4

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
        assert target.curr_offset == -8


class TestInstructionUpdate:
    @pytest.mark.parametrize(
        "instr",
        [
            AsmRetNode(start_position=25),
            AsmAllocateStackNode(start_position=99, stack_size=126),
            AsmCdqNode(start_position=123512),
        ],
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

        mov_node = AsmMovNode(start_position=31, src=pseudo_op0, dst=pseudo_op1)

        target.update_instruction(mov_node)
        assert mov_node.start_position == 31
        assert mov_node.src == AsmStackNode(start_position=312, offset=-4)
        assert mov_node.dst == AsmStackNode(start_position=313, offset=-8)

    @pytest.mark.parametrize("op", [AsmNot(start_position=13), AsmNeg(start_position=14)])
    def test_unary(self, op: AsmUnaryOperator):
        target = PseudoRegisterReplacer()

        pseudo_op0 = AsmPseudoRegisterNode(start_position=315, identifier="temp.0")
        unary_node = AsmUnaryNode(start_position=32, operator=op, src=pseudo_op0)

        target.update_instruction(unary_node)
        assert unary_node.start_position == 32
        assert unary_node.operator == op
        assert unary_node.src == AsmStackNode(start_position=315, offset=-4)

    @pytest.mark.parametrize(
        "op",
        [AsmAdd(start_position=1), AsmSubtract(start_position=1), AsmMultiply(start_position=1)],
    )
    def test_binary(self, op: AsmBinaryOperator):
        target = PseudoRegisterReplacer()

        pseudo_src = AsmPseudoRegisterNode(start_position=314, identifier="temp.0")
        pseudo_dst = AsmPseudoRegisterNode(start_position=315, identifier="temp.1")
        binary_node = AsmBinaryNode(start_position=100, operator=op, src=pseudo_src, dst=pseudo_dst)

        target.update_instruction(binary_node)
        assert binary_node.start_position == 100
        assert binary_node.operator == op
        assert binary_node.operator.start_position == 1
        assert binary_node.src == AsmStackNode(start_position=314, offset=-4)
        assert binary_node.dst == AsmStackNode(start_position=315, offset=-8)

    def test_idiv(self):
        target = PseudoRegisterReplacer()

        pseudo_src = AsmPseudoRegisterNode(start_position=129, identifier="temp.0")
        idiv_node = AsmIDivNode(start_position=31, src=pseudo_src)

        target.update_instruction(idiv_node)
        assert idiv_node.start_position == 31
        assert idiv_node.src == AsmStackNode(start_position=129, offset=-4)


class TestFunctionUpdate:
    def test_simple(self):
        source = "   int main(void) {return -    508;}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_function(token_tape)
        tg = TackyGenerator()
        tacky_func = tg.emit_function(src_node)
        asm_func = convert_tacky_function(tacky_func)

        target = PseudoRegisterReplacer()

        target.pseudo_replace_function(asm_func)
        assert len(asm_func.instructions) == 4
        assert asm_func.stack_size == 4

        i0 = asm_func.instructions[0]
        assert i0 == AsmMovNode(
            start_position=26,
            src=AsmImmediateIntNode(start_position=31, value=508),
            dst=AsmStackNode(start_position=26, offset=-4),
        )

        i1 = asm_func.instructions[1]
        assert i1 == AsmUnaryNode(start_position=26, operator=AsmNeg(start_position=26), src=i0.dst)

        i2 = asm_func.instructions[2]
        assert i2 == AsmMovNode(
            start_position=19,
            src=i1.src,
            dst=AsmRegisterNode(start_position=19, value="AX"),
        )

        i3 = asm_func.instructions[3]
        assert i3 == AsmRetNode(start_position=19)

    def test_simple_add(self):
        source = "   int main(void) {return 1 + 4;}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_function(token_tape)
        tg = TackyGenerator()
        tacky_func = tg.emit_function(src_node)
        asm_func = convert_tacky_function(tacky_func)

        target = PseudoRegisterReplacer()

        target.pseudo_replace_function(asm_func)
        assert len(asm_func.instructions) == 4
        assert asm_func.stack_size == 4

        i0 = asm_func.instructions[0]
        assert i0 == AsmMovNode(
            start_position=28,
            src=AsmImmediateIntNode(start_position=26, value=1),
            dst=AsmStackNode(start_position=28, offset=-4),
        )

        i1 = asm_func.instructions[1]
        assert i1 == AsmBinaryNode(
            start_position=28,
            operator=AsmAdd(start_position=28),
            src=AsmImmediateIntNode(start_position=30, value=4),
            dst=i1.dst,
        )

        i2 = asm_func.instructions[2]
        assert i2 == AsmMovNode(
            start_position=19,
            src=i1.dst,
            dst=AsmRegisterNode(start_position=19, value="AX"),
        )

        i3 = asm_func.instructions[3]
        assert i3 == AsmRetNode(start_position=19)


class TestProgramUpdate:
    def test_simple(self):
        source = "   int main(void) {return ~(   -509);}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_program(token_tape)
        tg = TackyGenerator()
        tacky_program = tg.emit_program(src_node)
        asm_prog = convert_tacky_program(tacky_program)

        target = PseudoRegisterReplacer()
        target.pseudo_replace(asm_prog)
        asm_func = asm_prog.function_definition
        assert asm_func.stack_size == 8
        assert len(asm_func.instructions) == 6

        i0 = asm_func.instructions[0]
        assert i0 == AsmMovNode(
            start_position=31,
            src=AsmImmediateIntNode(start_position=32, value=509),
            dst=AsmStackNode(start_position=31, offset=-4),
        )

        i1 = asm_func.instructions[1]
        assert i1 == AsmUnaryNode(start_position=31, operator=AsmNeg(start_position=31), src=i0.dst)

        i2 = asm_func.instructions[2]
        assert i2 == AsmMovNode(
            start_position=26,
            src=i1.src,
            dst=AsmStackNode(start_position=26, offset=-8),
        )

        i3 = asm_func.instructions[3]
        assert i3 == AsmUnaryNode(
            start_position=26,
            operator=AsmNot(start_position=26, source=i2.dst),
            src=i2.dst,
        )

        i4 = asm_func.instructions[4]
        assert i4 == AsmMovNode(
            start_position=19,
            src=i3.src,
            dst=AsmRegisterNode(start_position=19, value="AX"),
        )

        i5 = asm_func.instructions[5]
        assert i5 == AsmRetNode(start_position=19)

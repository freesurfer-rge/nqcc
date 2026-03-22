import pytest

from nqcc.codegen import (
    AsmAdd,
    AsmBinaryNode,
    AsmBitwiseAnd,
    AsmBitwiseOr,
    AsmBitwiseXor,
    AsmCdqNode,
    AsmFunctionNode,
    AsmIDivNode,
    AsmImmediateIntNode,
    AsmMovNode,
    AsmMultiply,
    AsmNeg,
    AsmNot,
    AsmProgramNode,
    AsmPseudoRegisterNode,
    AsmRegisterNode,
    AsmRetNode,
    AsmSubtract,
    AsmUnaryNode,
    convert_tacky_binary_operator,
    convert_tacky_function,
    convert_tacky_instruction,
    convert_tacky_operand,
    convert_tacky_program,
    convert_tacky_unary_operator,
)
from nqcc.parser import TokenTape, parse_function, parse_program
from nqcc.tacky import (
    TackyAdd,
    TackyBinaryNode,
    TackyBitwiseAnd,
    TackyBitwiseOr,
    TackyBitwiseXor,
    TackyComplement,
    TackyConstantIntNode,
    TackyDivide,
    TackyGenerator,
    TackyModulo,
    TackyMultiply,
    TackyNegate,
    TackyReturnNode,
    TackySubtract,
    TackyUnaryNode,
    TackyVarNode,
)


class TestConvertOperands:
    def test_constant_int(self):
        target = TackyConstantIntNode(start_position=123, value=345)
        result = convert_tacky_operand(target)
        assert isinstance(result, AsmImmediateIntNode)
        assert result.start_position == target.start_position
        assert result.value == target.value

    def test_var(self):
        target = TackyVarNode(start_position=222, identifier="my.value.0")
        result = convert_tacky_operand(target)
        assert isinstance(result, AsmPseudoRegisterNode)
        assert result.start_position == target.start_position
        assert result.identifier == target.identifier


class TestUnaryOperators:
    def test_negate(self):
        target = TackyNegate(start_position=462)
        result = convert_tacky_unary_operator(target)
        assert isinstance(result, AsmNeg)
        assert result.start_position == target.start_position

    def test_complement(self):
        target = TackyComplement(start_position=4251)
        result = convert_tacky_unary_operator(target)
        assert isinstance(result, AsmNot)
        assert result.start_position == target.start_position


class TestBinaryOperators:
    def test_add(self):
        target = TackyAdd(start_position=283)
        result = convert_tacky_binary_operator(target)
        assert result == AsmAdd(start_position=283)

    def test_subtract(self):
        target = TackySubtract(start_position=2183)
        result = convert_tacky_binary_operator(target)
        assert result == AsmSubtract(start_position=2183)

    def test_multiply(self):
        target = TackyMultiply(start_position=21831)
        result = convert_tacky_binary_operator(target)
        assert result == AsmMultiply(start_position=21831)

    def test_bitwiseand(self):
        target = TackyBitwiseAnd(start_position=623)
        result = convert_tacky_binary_operator(target)
        assert result == AsmBitwiseAnd(start_position=623)

    def test_bitwiseor(self):
        target = TackyBitwiseOr(start_position=6213)
        result = convert_tacky_binary_operator(target)
        assert result == AsmBitwiseOr(start_position=6213)

    def test_bitwisexor(self):
        target = TackyBitwiseXor(start_position=1623)
        result = convert_tacky_binary_operator(target)
        assert result == AsmBitwiseXor(start_position=1623)


class TestInstructions:
    def test_return(self):
        target = TackyReturnNode(
            start_position=345, value=TackyConstantIntNode(start_position=465, value=10)
        )
        result = convert_tacky_instruction(target)
        assert len(result) == 2
        assert result[0] == AsmMovNode(
            start_position=345,
            src=AsmImmediateIntNode(start_position=465, value=10),
            dst=AsmRegisterNode(start_position=345, value="eax"),
        )
        assert result[1] == AsmRetNode(start_position=345)

    def test_unary(self):
        target = TackyUnaryNode(
            start_position=123,
            operator=TackyComplement(start_position=1234),
            src=TackyVarNode(start_position=12345, identifier="tmp.0"),
            dst=TackyVarNode(start_position=123456, identifier="tmp.1"),
        )
        result = convert_tacky_instruction(target)
        assert len(result) == 2
        assert result[0] == AsmMovNode(
            start_position=123,
            src=AsmPseudoRegisterNode(start_position=12345, identifier="tmp.0"),
            dst=AsmPseudoRegisterNode(start_position=123456, identifier="tmp.1"),
        )
        assert result[1] == AsmUnaryNode(
            start_position=123,
            operator=AsmNot(start_position=1234),
            src=result[0].dst,
        )

    def test_add(self):
        target = TackyBinaryNode(
            start_position=22,
            operator=TackyAdd(start_position=21),
            left=TackyVarNode(start_position=12, identifier="left.0"),
            right=TackyVarNode(start_position=13, identifier="right.0"),
            dst=TackyVarNode(start_position=14, identifier="dst.0"),
        )

        result = convert_tacky_instruction(target)
        assert len(result) == 2
        assert result[0] == AsmMovNode(
            start_position=22,
            src=AsmPseudoRegisterNode(start_position=12, identifier="left.0"),
            dst=AsmPseudoRegisterNode(start_position=14, identifier="dst.0"),
        )
        assert result[1] == AsmBinaryNode(
            start_position=22,
            operator=AsmAdd(start_position=21),
            src=AsmPseudoRegisterNode(start_position=13, identifier="right.0"),
            dst=result[0].dst,
        )

    def test_subtract(self):
        target = TackyBinaryNode(
            start_position=22,
            operator=TackySubtract(start_position=21),
            left=TackyVarNode(start_position=12, identifier="left.0"),
            right=TackyVarNode(start_position=13, identifier="right.0"),
            dst=TackyVarNode(start_position=14, identifier="dst.0"),
        )

        result = convert_tacky_instruction(target)
        assert len(result) == 2
        assert result[0] == AsmMovNode(
            start_position=22,
            src=AsmPseudoRegisterNode(start_position=12, identifier="left.0"),
            dst=AsmPseudoRegisterNode(start_position=14, identifier="dst.0"),
        )
        assert result[1] == AsmBinaryNode(
            start_position=22,
            operator=AsmSubtract(start_position=21),
            src=AsmPseudoRegisterNode(start_position=13, identifier="right.0"),
            dst=result[0].dst,
        )

    def test_multiply(self):
        target = TackyBinaryNode(
            start_position=22,
            operator=TackyMultiply(start_position=21),
            left=TackyVarNode(start_position=12, identifier="left.0"),
            right=TackyVarNode(start_position=13, identifier="right.0"),
            dst=TackyVarNode(start_position=14, identifier="dst.0"),
        )

        result = convert_tacky_instruction(target)
        assert len(result) == 2
        assert result[0] == AsmMovNode(
            start_position=22,
            src=AsmPseudoRegisterNode(start_position=12, identifier="left.0"),
            dst=AsmPseudoRegisterNode(start_position=14, identifier="dst.0"),
        )
        assert result[1] == AsmBinaryNode(
            start_position=22,
            operator=AsmMultiply(start_position=21),
            src=AsmPseudoRegisterNode(start_position=13, identifier="right.0"),
            dst=result[0].dst,
        )

    @pytest.mark.parametrize("operation", ["&", "|", "^"])
    def test_bitwise(self, operation):
        _TACKY_OP = {"&": TackyBitwiseAnd, "|": TackyBitwiseOr, "^": TackyBitwiseXor}
        _ASM_OP = {"&": AsmBitwiseAnd, "|": AsmBitwiseOr, "^": AsmBitwiseXor}
        target = TackyBinaryNode(
            start_position=22,
            operator=_TACKY_OP[operation](start_position=21),
            left=TackyVarNode(start_position=12, identifier="left.0"),
            right=TackyVarNode(start_position=13, identifier="right.0"),
            dst=TackyVarNode(start_position=14, identifier="dst.0"),
        )

        result = convert_tacky_instruction(target)
        assert len(result) == 2
        assert result[0] == AsmMovNode(
            start_position=22,
            src=AsmPseudoRegisterNode(start_position=12, identifier="left.0"),
            dst=AsmPseudoRegisterNode(start_position=14, identifier="dst.0"),
        )
        assert result[1] == AsmBinaryNode(
            start_position=22,
            operator=_ASM_OP[operation](start_position=21),
            src=AsmPseudoRegisterNode(start_position=13, identifier="right.0"),
            dst=result[0].dst,
        )

    def test_divide(self):
        target = TackyBinaryNode(
            start_position=22,
            operator=TackyDivide(start_position=21),
            left=TackyVarNode(start_position=12, identifier="left.0"),
            right=TackyVarNode(start_position=13, identifier="right.0"),
            dst=TackyVarNode(start_position=14, identifier="dst.0"),
        )

        result = convert_tacky_instruction(target)
        assert len(result) == 4
        assert result[0] == AsmMovNode(
            start_position=22,
            src=AsmPseudoRegisterNode(start_position=12, identifier="left.0"),
            dst=AsmRegisterNode(start_position=22, value="eax"),
        )
        assert result[1] == AsmCdqNode(start_position=22)
        assert result[2] == AsmIDivNode(
            start_position=22, src=AsmPseudoRegisterNode(start_position=13, identifier="right.0")
        )
        assert result[3] == AsmMovNode(
            start_position=22,
            src=AsmRegisterNode(start_position=22, value="eax"),
            dst=AsmPseudoRegisterNode(start_position=14, identifier="dst.0"),
        )

    def test_modulo(self):
        target = TackyBinaryNode(
            start_position=22,
            operator=TackyModulo(start_position=21),
            left=TackyVarNode(start_position=12, identifier="left.0"),
            right=TackyVarNode(start_position=13, identifier="right.0"),
            dst=TackyVarNode(start_position=14, identifier="dst.0"),
        )

        result = convert_tacky_instruction(target)
        assert len(result) == 4
        assert result[0] == AsmMovNode(
            start_position=22,
            src=AsmPseudoRegisterNode(start_position=12, identifier="left.0"),
            dst=AsmRegisterNode(start_position=22, value="eax"),
        )
        assert result[1] == AsmCdqNode(start_position=22)
        assert result[2] == AsmIDivNode(
            start_position=22, src=AsmPseudoRegisterNode(start_position=13, identifier="right.0")
        )
        assert result[3] == AsmMovNode(
            start_position=22,
            src=AsmRegisterNode(start_position=22, value="edx"),
            dst=AsmPseudoRegisterNode(start_position=14, identifier="dst.0"),
        )


class TestFunctions:
    def test_simple(self):
        source = "   int main(void) {return -    508;}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_function(token_tape)

        tg = TackyGenerator()
        tacky_func = tg.emit_function(src_node)

        asm_func = convert_tacky_function(tacky_func)
        assert isinstance(asm_func, AsmFunctionNode)
        assert asm_func.start_position == 3
        assert asm_func.identifier == "main"
        assert len(asm_func.instructions) == 4

        i0 = asm_func.instructions[0]
        assert i0 == AsmMovNode(
            start_position=26,
            src=AsmImmediateIntNode(start_position=31, value=508),
            dst=AsmPseudoRegisterNode(start_position=26, identifier="tmp.main.0"),
        )

        i1 = asm_func.instructions[1]
        assert i1 == AsmUnaryNode(start_position=26, operator=AsmNeg(start_position=26), src=i0.dst)

        i2 = asm_func.instructions[2]
        assert i2 == AsmMovNode(
            start_position=19,
            src=i1.src,
            dst=AsmRegisterNode(start_position=19, value="eax"),
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
        assert isinstance(asm_func, AsmFunctionNode)
        assert asm_func.start_position == 3
        assert asm_func.identifier == "main"
        assert len(asm_func.instructions) == 4

        i0 = asm_func.instructions[0]
        assert i0 == AsmMovNode(
            start_position=28,
            src=AsmImmediateIntNode(start_position=26, value=1),
            dst=AsmPseudoRegisterNode(start_position=28, identifier="tmp.main.0"),
        )

        i1 = asm_func.instructions[1]
        assert i1 == AsmBinaryNode(
            start_position=28,
            operator=AsmAdd(start_position=28),
            src=AsmImmediateIntNode(start_position=30, value=4),
            dst=AsmPseudoRegisterNode(start_position=28, identifier="tmp.main.0"),
        )

        i2 = asm_func.instructions[2]
        assert i2 == AsmMovNode(
            start_position=19,
            src=i1.dst,
            dst=AsmRegisterNode(start_position=19, value="eax"),
        )

        i3 = asm_func.instructions[3]
        assert i3 == AsmRetNode(start_position=19)


class TestPrograms:
    def test_simple(self):
        source = "   int main(void) {return ~(    509);}"
        token_tape = TokenTape.from_c_source(source)
        src_node = parse_program(token_tape)

        tg = TackyGenerator()
        tacky_program = tg.emit_program(src_node)

        asm_prog = convert_tacky_program(tacky_program)
        assert isinstance(asm_prog, AsmProgramNode)
        assert asm_prog.start_position == 0

        asm_func = asm_prog.function_definition
        assert asm_func.start_position == 3
        assert asm_func.identifier == "main"
        assert len(asm_func.instructions) == 4

        i0 = asm_func.instructions[0]
        assert i0 == AsmMovNode(
            start_position=26,
            src=AsmImmediateIntNode(start_position=32, value=509),
            dst=AsmPseudoRegisterNode(start_position=26, identifier="tmp.main.0"),
        )

        i1 = asm_func.instructions[1]
        assert i1 == AsmUnaryNode(start_position=26, operator=AsmNot(start_position=26), src=i0.dst)

        i2 = asm_func.instructions[2]
        assert i2 == AsmMovNode(
            start_position=19,
            src=i1.src,
            dst=AsmRegisterNode(start_position=19, value="eax"),
        )

        i3 = asm_func.instructions[3]
        assert i3 == AsmRetNode(start_position=19)

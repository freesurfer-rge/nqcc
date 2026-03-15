from nqcc.codegen import (
    AsmFunctionNode,
    AsmImmediateIntNode,
    AsmMovNode,
    AsmNegOperator,
    AsmNotOperator,
    AsmProgramNode,
    AsmPseudoRegisterNode,
    AsmRegisterNode,
    AsmRetNode,
    AsmUnaryNode,
    AsmBinaryNode,
    AsmBinaryOperator,
    AsmAdd,
    AsmSubtract,
    AsmMultiply,
    AsmIDivNode,
    AsmCdqNode,
    convert_tacky_function,
    convert_tacky_instruction,
    convert_tacky_operand,
    convert_tacky_program,
    convert_tacky_unary_operator,
    convert_tacky_binary_operator,
    convert_tacky_binary_node,
)
from nqcc.parser import TokenTape, parse_function, parse_program
from nqcc.tacky import (
    TackyComplementNode,
    TackyConstantIntNode,
    TackyGenerator,
    TackyNegateNode,
    TackyReturnNode,
    TackyUnaryNode,
    TackyVarNode,
    TackyAdd,
    TackySubtract,
    TackyMultiply,
    TackyBinaryNode,
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
        target = TackyNegateNode(start_position=462)
        result = convert_tacky_unary_operator(target)
        assert isinstance(result, AsmNegOperator)
        assert result.start_position == target.start_position

    def test_complement(self):
        target = TackyComplementNode(start_position=4251)
        result = convert_tacky_unary_operator(target)
        assert isinstance(result, AsmNotOperator)
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


class TestInstructions:
    def test_return(self):
        target = TackyReturnNode(
            start_position=345, value=TackyConstantIntNode(start_position=465, value=10)
        )
        result = convert_tacky_instruction(target)
        assert len(result) == 2
        assert result[0] == AsmMovNode(
            start_position=345,
            source=AsmImmediateIntNode(start_position=465, value=10),
            destination=AsmRegisterNode(start_position=345, value="eax"),
        )
        assert result[1] == AsmRetNode(start_position=345)

    def test_unary(self):
        target = TackyUnaryNode(
            start_position=123,
            operator=TackyComplementNode(start_position=1234),
            src=TackyVarNode(start_position=12345, identifier="tmp.0"),
            dst=TackyVarNode(start_position=123456, identifier="tmp.1"),
        )
        result = convert_tacky_instruction(target)
        assert len(result) == 2
        assert result[0] == AsmMovNode(
            start_position=123,
            source=AsmPseudoRegisterNode(start_position=12345, identifier="tmp.0"),
            destination=AsmPseudoRegisterNode(start_position=123456, identifier="tmp.1"),
        )
        assert result[1] == AsmUnaryNode(
            start_position=123,
            operator=AsmNotOperator(start_position=1234),
            source=result[0].destination,
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
            source=AsmPseudoRegisterNode(start_position=12, identifier="left.0"),
            destination=AsmPseudoRegisterNode(start_position=14, identifier="dst.0"),
        )
        assert result[1] == AsmBinaryNode(
            start_position=22,
            operator=AsmAdd(start_position=21),
            src=AsmPseudoRegisterNode(start_position=13, identifier="right.0"),
            dst=result[0].destination,
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
            source=AsmImmediateIntNode(start_position=31, value=508),
            destination=AsmPseudoRegisterNode(start_position=26, identifier="tmp.main.0"),
        )

        i1 = asm_func.instructions[1]
        assert i1 == AsmUnaryNode(
            start_position=26, operator=AsmNegOperator(start_position=26), source=i0.destination
        )

        i2 = asm_func.instructions[2]
        assert i2 == AsmMovNode(
            start_position=19,
            source=i1.source,
            destination=AsmRegisterNode(start_position=19, value="eax"),
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
            source=AsmImmediateIntNode(start_position=32, value=509),
            destination=AsmPseudoRegisterNode(start_position=26, identifier="tmp.main.0"),
        )

        i1 = asm_func.instructions[1]
        assert i1 == AsmUnaryNode(
            start_position=26, operator=AsmNotOperator(start_position=26), source=i0.destination
        )

        i2 = asm_func.instructions[2]
        assert i2 == AsmMovNode(
            start_position=19,
            source=i1.source,
            destination=AsmRegisterNode(start_position=19, value="eax"),
        )

        i3 = asm_func.instructions[3]
        assert i3 == AsmRetNode(start_position=19)

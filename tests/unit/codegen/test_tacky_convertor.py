from nqcc.codegen import (
    AsmImmediateIntNode,
    AsmNegOperator,
    AsmNotOperator,
    AsmPseudoRegisterNode,
    AsmMovNode,
    AsmRetNode,
    convert_tacky_operand,
    convert_tacky_unary_operator,
    convert_tacky_instruction,
    AsmRegisterNode,
)
from nqcc.tacky import (
    TackyComplementNode,
    TackyConstantIntNode,
    TackyNegateNode,
    TackyVarNode,
    TackyReturnNode,
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

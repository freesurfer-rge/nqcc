from nqcc.codegen import (
    AsmImmediateIntNode,
    AsmNegOperator,
    AsmNotOperator,
    AsmPseudoRegisterNode,
    convert_tacky_operand,
    convert_tacky_unary_operator,
)
from nqcc.tacky import TackyComplementNode, TackyConstantIntNode, TackyNegateNode, TackyVarNode


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

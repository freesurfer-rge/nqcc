from nqcc.codegen import (
    AsmAdd,
    AsmBitwiseAnd,
    AsmBitwiseOr,
    AsmBitwiseXor,
    AsmLeftShift,
    AsmMultiply,
    AsmNeg,
    AsmNot,
    AsmRightShift,
    AsmSubtract,
    convert_tacky_binary_operator,
    convert_tacky_unary_operator,
)
from nqcc.frontend.tacky import (
    TackyAdd,
    TackyBitwiseAnd,
    TackyBitwiseOr,
    TackyBitwiseXor,
    TackyComplement,
    TackyLeftShift,
    TackyMultiply,
    TackyNegate,
    TackyRightShift,
    TackySubtract,
)


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

    def test_leftshift(self):
        target = TackyLeftShift(start_position=11623)
        result = convert_tacky_binary_operator(target)
        assert result == AsmLeftShift(start_position=11623)

    def test_rightshift(self):
        target = TackyRightShift(start_position=11623)
        result = convert_tacky_binary_operator(target)
        assert result == AsmRightShift(start_position=11623)

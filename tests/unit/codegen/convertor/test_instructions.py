import pytest

from nqcc.codegen import (
    AsmAdd,
    AsmBinaryNode,
    AsmBitwiseAnd,
    AsmBitwiseOr,
    AsmBitwiseXor,
    AsmCdqNode,
    AsmIDivNode,
    AsmImmediateIntNode,
    AsmLeftShift,
    AsmMovNode,
    AsmMultiply,
    AsmNot,
    AsmPseudoRegisterNode,
    AsmRegisterNode,
    AsmRetNode,
    AsmRightShift,
    AsmSubtract,
    AsmUnaryNode,
    convert_tacky_instruction,
)
from nqcc.tacky import (
    TackyAdd,
    TackyBinaryNode,
    TackyBitwiseAnd,
    TackyBitwiseOr,
    TackyBitwiseXor,
    TackyComplement,
    TackyConstantIntNode,
    TackyDivide,
    TackyLeftShift,
    TackyModulo,
    TackyMultiply,
    TackyReturnNode,
    TackyRightShift,
    TackySubtract,
    TackyUnaryNode,
    TackyVarNode,
)


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

    @pytest.mark.parametrize("operation", ["<<", ">>"])
    def test_shift(self, operation):
        _TACKY_OP = {
            "<<": TackyLeftShift,
            ">>": TackyRightShift,
        }
        _ASM_OP = {
            "<<": AsmLeftShift,
            ">>": AsmRightShift,
        }
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

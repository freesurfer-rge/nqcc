from typing import Type

import pytest
from nqcc.codegen import (
    AsmAdd,
    AsmBinaryNode,
    AsmBitwiseAnd,
    AsmBitwiseOr,
    AsmBitwiseXor,
    AsmCdqNode,
    AsmCmpNode,
    AsmCondCode,
    AsmIDivNode,
    AsmImmediateIntNode,
    AsmJmpCCNode,
    AsmJmpNode,
    AsmLabelNode,
    AsmLeftShift,
    AsmMovNode,
    AsmMultiply,
    AsmNeg,
    AsmNot,
    AsmPseudoRegisterNode,
    AsmRegisterNode,
    AsmRetNode,
    AsmRightShift,
    AsmSetCCNode,
    AsmSubtract,
    AsmUnaryNode,
    AsmUnaryOperator,
    convert_tacky_instruction,
)
from nqcc.frontend.tacky import (
    TackyAdd,
    TackyBinaryNode,
    TackyBinaryOperator,
    TackyBitwiseAnd,
    TackyBitwiseOr,
    TackyBitwiseXor,
    TackyComplement,
    TackyConstantIntNode,
    TackyCopyNode,
    TackyDivide,
    TackyEqualTo,
    TackyGreaterThan,
    TackyGreaterThanOrEqual,
    TackyJumpIfNotZeroNode,
    TackyJumpIfZeroNode,
    TackyJumpNode,
    TackyLabelNode,
    TackyLeftShift,
    TackyLessThan,
    TackyLessThanOrEqual,
    TackyLogicalNot,
    TackyModulo,
    TackyMultiply,
    TackyNegate,
    TackyNotEqualTo,
    TackyReturnNode,
    TackyRightShift,
    TackySubtract,
    TackyUnaryNode,
    TackyUnaryOperator,
    TackyVarNode,
)

_COND_CODE_MAP: dict[Type[TackyBinaryOperator], AsmCondCode] = {
    TackyEqualTo: "E",
    TackyNotEqualTo: "NE",
    TackyGreaterThan: "G",
    TackyGreaterThanOrEqual: "GE",
    TackyLessThan: "L",
    TackyLessThanOrEqual: "LE",
}


class TestUnaryInstructions:
    @pytest.mark.parametrize(
        ("tacky_operator", "asm_operator"), [(TackyComplement, AsmNot), (TackyNegate, AsmNeg)]
    )
    def test_unary_arithmetic(
        self, tacky_operator: Type[TackyUnaryOperator], asm_operator: Type[AsmUnaryOperator]
    ):
        target = TackyUnaryNode(
            start_position=123,
            operator=tacky_operator(start_position=1234),
            src=TackyVarNode(start_position=12345, identifier="tmp.0"),
            dst=TackyVarNode(start_position=123456, identifier="tmp.1"),
        )
        result = convert_tacky_instruction(target)
        assert len(result) == 2
        assert isinstance(result[0], AsmMovNode)
        assert result[0] == AsmMovNode(
            start_position=123,
            src=AsmPseudoRegisterNode(start_position=12345, identifier="tmp.0"),
            dst=AsmPseudoRegisterNode(start_position=123456, identifier="tmp.1"),
        )
        assert result[1] == AsmUnaryNode(
            start_position=123,
            operator=asm_operator(start_position=1234),
            src=result[0].dst,
        )

    def test_unary_logical_not(self):
        target = TackyUnaryNode(
            start_position=123,
            operator=TackyLogicalNot(start_position=1234),
            src=TackyVarNode(start_position=12345, identifier="tmp.0"),
            dst=TackyVarNode(start_position=123456, identifier="tmp.1"),
        )
        result = convert_tacky_instruction(target)
        assert len(result) == 3
        assert result[0] == AsmCmpNode(
            start_position=123,
            src=AsmImmediateIntNode(start_position=123, value=0),
            dst=AsmPseudoRegisterNode(start_position=12345, identifier="tmp.0"),
        )
        assert isinstance(result[1], AsmMovNode)
        assert result[1] == AsmMovNode(
            start_position=123,
            src=AsmImmediateIntNode(start_position=123, value=0),
            dst=AsmPseudoRegisterNode(start_position=123456, identifier="tmp.1"),
        )
        assert result[2] == AsmSetCCNode(start_position=123, src=result[1].dst, cond_code="E")


class TestJumpInstructions:
    def test_jump(self):
        target = TackyJumpNode(start_position=123, target="jump.0")

        result = convert_tacky_instruction(target)
        assert len(result) == 1
        assert result[0] == AsmJmpNode(start_position=123, target="jump.0")

    def test_jmp_zero(self):
        target = TackyJumpIfZeroNode(
            start_position=23,
            target="jmp_zero.0",
            condition=TackyVarNode(start_position=1245, identifier="tmp.0"),
        )

        result = convert_tacky_instruction(target)
        assert len(result) == 2
        assert result[0] == AsmCmpNode(
            start_position=23,
            src=AsmImmediateIntNode(start_position=23, value=0),
            dst=AsmPseudoRegisterNode(start_position=1245, identifier="tmp.0"),
        )
        assert result[1] == AsmJmpCCNode(start_position=23, target="jmp_zero.0", cond_code="E")

    def test_jmp_notzero(self):
        target = TackyJumpIfNotZeroNode(
            start_position=23,
            target="jmp_notzero.0",
            condition=TackyVarNode(start_position=1245, identifier="tmp.0"),
        )

        result = convert_tacky_instruction(target)
        assert len(result) == 2
        assert result[0] == AsmCmpNode(
            start_position=23,
            src=AsmImmediateIntNode(start_position=23, value=0),
            dst=AsmPseudoRegisterNode(start_position=1245, identifier="tmp.0"),
        )
        assert result[1] == AsmJmpCCNode(start_position=23, target="jmp_notzero.0", cond_code="NE")

    def test_label(self):
        target = TackyLabelNode(start_position=138, identifier="something.or.other")

        result = convert_tacky_instruction(target)
        assert len(result) == 1
        assert result[0] == AsmLabelNode(start_position=138, identifier="something.or.other")


class TestBinaryInstructions:
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
            dst=AsmRegisterNode(start_position=22, value="AX"),
        )
        assert result[1] == AsmCdqNode(start_position=22)
        assert result[2] == AsmIDivNode(
            start_position=22, src=AsmPseudoRegisterNode(start_position=13, identifier="right.0")
        )
        assert result[3] == AsmMovNode(
            start_position=22,
            src=AsmRegisterNode(start_position=22, value="AX"),
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
            dst=AsmRegisterNode(start_position=22, value="AX"),
        )
        assert result[1] == AsmCdqNode(start_position=22)
        assert result[2] == AsmIDivNode(
            start_position=22, src=AsmPseudoRegisterNode(start_position=13, identifier="right.0")
        )
        assert result[3] == AsmMovNode(
            start_position=22,
            src=AsmRegisterNode(start_position=22, value="DX"),
            dst=AsmPseudoRegisterNode(start_position=14, identifier="dst.0"),
        )

    @pytest.mark.parametrize(
        "op",
        [
            TackyEqualTo,
            TackyNotEqualTo,
            TackyGreaterThan,
            TackyGreaterThanOrEqual,
            TackyLessThan,
            TackyLessThanOrEqual,
        ],
    )
    def test_comparisons(self, op: Type):
        target = TackyBinaryNode(
            start_position=23,
            operator=op(start_position=24),
            left=TackyVarNode(start_position=12, identifier="left.0"),
            right=TackyVarNode(start_position=13, identifier="right.0"),
            dst=TackyVarNode(start_position=14, identifier="dst.0"),
        )

        result = convert_tacky_instruction(target)
        assert len(result) == 3

        assert result[0] == AsmCmpNode(
            start_position=23,
            src=AsmPseudoRegisterNode(start_position=13, identifier="right.0"),
            dst=AsmPseudoRegisterNode(start_position=12, identifier="left.0"),
        )
        assert isinstance(result[1], AsmMovNode)
        assert result[1] == AsmMovNode(
            start_position=23,
            src=AsmImmediateIntNode(start_position=23, value=0),
            dst=AsmPseudoRegisterNode(start_position=14, identifier="dst.0"),
        )
        assert result[2] == AsmSetCCNode(
            start_position=23, src=result[1].dst, cond_code=_COND_CODE_MAP[op]
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
            dst=AsmRegisterNode(start_position=345, value="AX"),
        )
        assert result[1] == AsmRetNode(start_position=345)

    def test_copy(self):
        target = TackyCopyNode(
            start_position=132,
            src=TackyVarNode(start_position=12, identifier="src.0"),
            dst=TackyVarNode(start_position=13, identifier="dst.0"),
        )

        result = convert_tacky_instruction(target)
        assert len(result) == 1
        assert result[0] == AsmMovNode(
            start_position=132,
            src=AsmPseudoRegisterNode(start_position=12, identifier="src.0"),
            dst=AsmPseudoRegisterNode(start_position=13, identifier="dst.0"),
        )

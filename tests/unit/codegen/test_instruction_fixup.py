import pytest

from nqcc.codegen import (
    AsmAdd,
    AsmAllocateStackNode,
    AsmBinaryNode,
    AsmBinaryOperator,
    AsmBitwiseAnd,
    AsmBitwiseOr,
    AsmBitwiseXor,
    AsmCmpNode,
    AsmFunctionNode,
    AsmIDivNode,
    AsmImmediateIntNode,
    AsmLeftShift,
    AsmMovNode,
    AsmMultiply,
    AsmOperandNode,
    AsmProgramNode,
    AsmRegisterNode,
    AsmRightShift,
    AsmStackNode,
    AsmSubtract,
    apply_binary_fixup,
    apply_cmp_fixup,
    apply_idiv_fixup,
    apply_mov_fixup,
    fixup_function_instructions,
    fixup_program_instructions,
)


class TestMovFixup:
    @pytest.mark.parametrize(
        ["src", "dst"],
        [
            (
                AsmRegisterNode(start_position=0, value="R10"),
                AsmRegisterNode(start_position=0, value="AX"),
            ),
            (
                AsmRegisterNode(start_position=0, value="R10"),
                AsmStackNode(start_position=0, offset=-4),
            ),
            (
                AsmStackNode(start_position=0, offset=-4),
                AsmRegisterNode(start_position=0, value="R10"),
            ),
        ],
    )
    def test_unaffected_node(self, src: AsmOperandNode, dst: AsmOperandNode):
        target = AsmMovNode(start_position=0, src=src, dst=dst)
        orig = target.model_copy(deep=True)

        fixed = apply_mov_fixup(target)
        assert len(fixed) == 1
        assert fixed[0] == orig

    def test_stack_stack_node(self):
        src = AsmStackNode(start_position=1, offset=-4)
        dst = AsmStackNode(start_position=2, offset=-8)
        target = AsmMovNode(start_position=0, src=src, dst=dst)

        fixed = apply_mov_fixup(target)
        assert len(fixed) == 2
        assert fixed[0] == AsmMovNode(
            start_position=0,
            src=src,
            dst=AsmRegisterNode(start_position=0, value="R10"),
        )
        assert fixed[1] == AsmMovNode(
            start_position=0,
            src=fixed[0].dst,
            dst=dst,
        )


class TestCmpFixup:
    def test_both_stackvar(self):
        src = AsmStackNode(start_position=1, offset=-4)
        dst = AsmStackNode(start_position=2, offset=-8)
        target = AsmCmpNode(start_position=0, src=src, dst=dst)

        fixed = apply_cmp_fixup(target)
        assert len(fixed) == 2
        assert fixed[0] == AsmMovNode(
            start_position=0,
            src=src,
            dst=AsmRegisterNode(start_position=0, value="R10"),
        )
        assert fixed[1] == AsmCmpNode(
            start_position=0,
            src=fixed[0].dst,
            dst=dst,
        )

    def test_dst_cmp(self):
        src = AsmRegisterNode(start_position=1, value="AX")
        dst = AsmImmediateIntNode(start_position=2, value=5)
        target = AsmCmpNode(start_position=0, src=src, dst=dst)

        fixed = apply_cmp_fixup(target)
        assert len(fixed) == 2
        assert fixed[0] == AsmMovNode(
            start_position=0,
            src=dst,
            dst=AsmRegisterNode(start_position=0, value="R11"),
        )
        assert fixed[1] == AsmCmpNode(
            start_position=0,
            src=src,
            dst=fixed[0].dst,
        )


class TestIDivFixup:
    @pytest.mark.parametrize(
        "src",
        [
            AsmRegisterNode(start_position=1, value="R10"),
            AsmStackNode(start_position=3, offset=-4),
        ],
    )
    def test_unaffected_node(self, src: AsmOperandNode):
        target = AsmIDivNode(start_position=31, src=src)
        orig = target.model_copy(deep=True)

        fixed = apply_idiv_fixup(target)
        assert len(fixed) == 1
        assert fixed[0] == orig

    def test_immediate_node(self):
        val = AsmImmediateIntNode(start_position=3, value=45)
        target = AsmIDivNode(start_position=4, src=val)

        fixed = apply_idiv_fixup(target)
        assert len(fixed) == 2
        assert fixed[0] == AsmMovNode(
            start_position=4,
            src=val,
            dst=AsmRegisterNode(start_position=4, value="R10"),
        )
        assert fixed[1] == AsmIDivNode(start_position=4, src=fixed[0].dst)


class TestBinaryFixup:
    @pytest.mark.parametrize(
        "op",
        [
            AsmAdd(start_position=3),
            AsmSubtract(start_position=3),
            AsmBitwiseAnd(start_position=3),
            AsmBitwiseOr(start_position=3),
            AsmBitwiseXor(start_position=3),
        ],
    )
    @pytest.mark.parametrize(
        "src",
        [
            AsmRegisterNode(start_position=2, value="R10"),
            AsmImmediateIntNode(start_position=2, value=1312),
        ],
    )
    def test_binopsrcfixup_unaffected(self, op: AsmBinaryOperator, src: AsmOperandNode):
        dst = AsmStackNode(start_position=2, offset=-8)
        target = AsmBinaryNode(start_position=4, operator=op, src=src, dst=dst)
        orig = target.model_copy(deep=True)

        fixed = apply_binary_fixup(target)
        assert len(fixed) == 1
        assert fixed[0] == orig

    @pytest.mark.parametrize(
        "op",
        [
            AsmAdd(start_position=3),
            AsmSubtract(start_position=3),
            AsmBitwiseAnd(start_position=3),
            AsmBitwiseOr(start_position=3),
            AsmBitwiseXor(start_position=3),
        ],
    )
    def test_binopsrcfixup_node(self, op: AsmBinaryOperator):
        src = AsmStackNode(start_position=1, offset=-4)
        dst = AsmStackNode(start_position=2, offset=-8)
        target = AsmBinaryNode(start_position=4, operator=op, src=src, dst=dst)

        fixed = apply_binary_fixup(target)
        assert len(fixed) == 2
        assert isinstance(fixed[0], AsmMovNode)
        assert fixed[0] == AsmMovNode(
            start_position=4,
            src=src,
            dst=AsmRegisterNode(start_position=4, value="R10"),
        )
        assert fixed[1] == AsmBinaryNode(start_position=4, operator=op, src=fixed[0].dst, dst=dst)

    @pytest.mark.parametrize(
        "op",
        [
            AsmLeftShift(start_position=3),
            AsmRightShift(start_position=3),
        ],
    )
    @pytest.mark.parametrize(
        "src",
        [
            AsmImmediateIntNode(start_position=2, value=1312),
        ],
    )
    def test_shift_unaffected(self, op: AsmBinaryOperator, src: AsmOperandNode):
        dst = AsmStackNode(start_position=2, offset=-8)
        target = AsmBinaryNode(start_position=4, operator=op, src=src, dst=dst)
        orig = target.model_copy(deep=True)

        fixed = apply_binary_fixup(target)
        assert len(fixed) == 1
        assert fixed[0] == orig

    @pytest.mark.parametrize(
        "op",
        [
            AsmLeftShift(start_position=3),
            AsmRightShift(start_position=3),
        ],
    )
    @pytest.mark.parametrize(
        "src",
        [
            AsmStackNode(start_position=2, offset=-4),
            AsmRegisterNode(start_position=2, value="R10"),
        ],
    )
    def test_shift_fixup(self, op: AsmBinaryOperator, src: AsmOperandNode):
        dst = AsmStackNode(start_position=2, offset=-8)
        target = AsmBinaryNode(start_position=4, operator=op, src=src, dst=dst)

        fixed = apply_binary_fixup(target)
        assert len(fixed) == 2
        assert isinstance(fixed[0], AsmMovNode)
        assert fixed[0] == AsmMovNode(
            start_position=4, src=src, dst=AsmRegisterNode(start_position=4, value="CX")
        )
        assert fixed[1] == AsmBinaryNode(start_position=4, operator=op, src=fixed[0].dst, dst=dst)

    def test_mul_unaffected(self):
        src = AsmImmediateIntNode(start_position=1, value=13)
        dst = AsmRegisterNode(start_position=2, value="R11")
        target = AsmBinaryNode(
            start_position=4, operator=AsmMultiply(start_position=3), src=src, dst=dst
        )
        orig = target.model_copy(deep=True)

        fixed = apply_binary_fixup(target)
        assert len(fixed) == 1
        assert fixed[0] == orig

    def test_mul_node(self):
        src = AsmImmediateIntNode(start_position=1, value=13)
        dst = AsmStackNode(start_position=2, offset=-8)
        target = AsmBinaryNode(
            start_position=4, operator=AsmMultiply(start_position=3), src=src, dst=dst
        )

        fixed = apply_binary_fixup(target)
        assert len(fixed) == 3
        assert fixed[0] == AsmMovNode(
            start_position=4,
            src=dst,
            dst=AsmRegisterNode(start_position=4, value="R11"),
        )
        assert fixed[1] == AsmBinaryNode(
            start_position=4,
            operator=AsmMultiply(start_position=3),
            src=src,
            dst=fixed[0].dst,
        )
        assert fixed[2] == AsmMovNode(start_position=4, src=fixed[0].dst, dst=dst)


class TestFunctionFixup:
    def test_simple(self):
        src = AsmStackNode(start_position=2, offset=-4)
        dst = AsmStackNode(start_position=3, offset=-8)
        target = AsmFunctionNode(
            start_position=0,
            identifier="abc",
            instructions=[AsmMovNode(start_position=1, src=src, dst=dst)],
            stack_size=8,
        )

        fixup_function_instructions(target)

        assert len(target.instructions) == 3
        i0 = target.instructions[0]
        assert i0 == AsmAllocateStackNode(start_position=0, stack_size=16)

        reg = AsmRegisterNode(start_position=1, value="R10")
        i1 = target.instructions[1]
        assert i1 == AsmMovNode(start_position=1, src=src, dst=reg)

        i2 = target.instructions[2]
        assert i2 == AsmMovNode(start_position=1, src=reg, dst=dst)

    def test_idiv(self):
        src = AsmImmediateIntNode(start_position=2, value=6)
        target = AsmFunctionNode(
            start_position=0,
            identifier="abc",
            instructions=[AsmIDivNode(start_position=1, src=src)],
            stack_size=8,
        )

        fixup_function_instructions(target)

        assert len(target.instructions) == 3
        i0 = target.instructions[0]
        assert i0 == AsmAllocateStackNode(start_position=0, stack_size=16)

        reg = AsmRegisterNode(start_position=1, value="R10")
        i1 = target.instructions[1]
        assert i1 == AsmMovNode(start_position=1, src=src, dst=reg)

        i2 = target.instructions[2]
        assert i2 == AsmIDivNode(start_position=1, src=reg)

    @pytest.mark.parametrize("op", [AsmAdd(start_position=55), AsmSubtract(start_position=66)])
    def test_addsub(self, op: AsmBinaryOperator):
        src = AsmStackNode(start_position=2, offset=-4)
        dst = AsmStackNode(start_position=3, offset=-8)
        target = AsmFunctionNode(
            start_position=0,
            identifier="abc",
            instructions=[AsmBinaryNode(start_position=1, operator=op, src=src, dst=dst)],
            stack_size=8,
        )

        fixup_function_instructions(target)

        assert len(target.instructions) == 3
        i0 = target.instructions[0]
        assert i0 == AsmAllocateStackNode(start_position=0, stack_size=16)

        reg = AsmRegisterNode(start_position=1, value="R10")
        i1 = target.instructions[1]
        assert i1 == AsmMovNode(start_position=1, src=src, dst=reg)

        i2 = target.instructions[2]
        assert i2 == AsmBinaryNode(start_position=1, operator=op, src=reg, dst=dst)

    def test_mul(self):
        src = AsmImmediateIntNode(start_position=2, value=3145)
        dst = AsmStackNode(start_position=3, offset=-8)
        target = AsmFunctionNode(
            start_position=0,
            identifier="abc",
            instructions=[
                AsmBinaryNode(
                    start_position=1, operator=AsmMultiply(start_position=5), src=src, dst=dst
                )
            ],
            stack_size=8,
        )

        fixup_function_instructions(target)

        assert len(target.instructions) == 4
        i0 = target.instructions[0]
        assert i0 == AsmAllocateStackNode(start_position=0, stack_size=16)

        reg = AsmRegisterNode(start_position=1, value="R11")
        i1 = target.instructions[1]
        assert i1 == AsmMovNode(start_position=1, src=dst, dst=reg)

        i2 = target.instructions[2]
        assert i2 == AsmBinaryNode(
            start_position=1, operator=AsmMultiply(start_position=5), src=src, dst=reg
        )

        i3 = target.instructions[3]
        assert i3 == AsmMovNode(start_position=1, src=reg, dst=dst)


class TestProgramFixup:
    def test_simple(self):
        src = AsmStackNode(start_position=2, offset=-4)
        dst = AsmStackNode(start_position=3, offset=-8)
        func = AsmFunctionNode(
            start_position=0,
            identifier="abc",
            instructions=[AsmMovNode(start_position=1, src=src, dst=dst)],
            stack_size=8,
        )

        target = AsmProgramNode(start_position=0, definitions=[func])

        fixup_program_instructions(target)

        # Just check that the expected increase has happened
        assert len(target.definitions[0].instructions) == 3

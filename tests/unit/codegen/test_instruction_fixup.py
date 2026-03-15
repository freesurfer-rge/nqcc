import pytest

from nqcc.codegen import (
    AsmAdd,
    AsmAllocateStackNode,
    AsmBinaryNode,
    AsmBinaryOperator,
    AsmFunctionNode,
    AsmIDivNode,
    AsmImmediateIntNode,
    AsmMovNode,
    AsmMultiply,
    AsmOperandNode,
    AsmProgramNode,
    AsmRegisterNode,
    AsmStackNode,
    AsmSubtract,
    apply_binary_fixup,
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
                AsmRegisterNode(start_position=0, value="r10d"),
                AsmRegisterNode(start_position=0, value="eax"),
            ),
            (
                AsmRegisterNode(start_position=0, value="r10d"),
                AsmStackNode(start_position=0, offset=-4),
            ),
            (
                AsmStackNode(start_position=0, offset=-4),
                AsmRegisterNode(start_position=0, value="r10d"),
            ),
        ],
    )
    def test_unaffected_node(self, src: AsmOperandNode, dst: AsmOperandNode):
        target = AsmMovNode(start_position=0, source=src, destination=dst)
        orig = target.model_copy(deep=True)

        fixed = apply_mov_fixup(target)
        assert len(fixed) == 1
        assert fixed[0] == orig

    def test_stack_stack_node(self):
        src = AsmStackNode(start_position=1, offset=-4)
        dst = AsmStackNode(start_position=2, offset=-8)
        target = AsmMovNode(start_position=0, source=src, destination=dst)

        fixed = apply_mov_fixup(target)
        assert len(fixed) == 2
        assert fixed[0] == AsmMovNode(
            start_position=0,
            source=src,
            destination=AsmRegisterNode(start_position=0, value="r10d"),
        )
        assert fixed[1] == AsmMovNode(
            start_position=0,
            source=fixed[0].destination,
            destination=dst,
        )


class TestIDivFixup:
    @pytest.mark.parametrize(
        "src",
        [
            AsmRegisterNode(start_position=1, value="r10d"),
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
            source=val,
            destination=AsmRegisterNode(start_position=4, value="r10d"),
        )
        assert fixed[1] == AsmIDivNode(start_position=4, src=fixed[0].destination)


class TestBinaryFixup:
    @pytest.mark.parametrize("op", [AsmAdd(start_position=3), AsmSubtract(start_position=3)])
    @pytest.mark.parametrize(
        "src",
        [
            AsmRegisterNode(start_position=2, value="r10d"),
            AsmImmediateIntNode(start_position=2, value=1312),
        ],
    )
    def test_addsub_unaffected(self, op: AsmBinaryOperator, src: AsmOperandNode):
        dst = AsmStackNode(start_position=2, offset=-8)
        target = AsmBinaryNode(start_position=4, operator=op, src=src, dst=dst)
        orig = target.model_copy(deep=True)

        fixed = apply_binary_fixup(target)
        assert len(fixed) == 1
        assert fixed[0] == orig

    @pytest.mark.parametrize("op", [AsmAdd(start_position=3), AsmSubtract(start_position=3)])
    def test_addsub_node(self, op: AsmBinaryOperator):
        src = AsmStackNode(start_position=1, offset=-4)
        dst = AsmStackNode(start_position=2, offset=-8)
        target = AsmBinaryNode(start_position=4, operator=op, src=src, dst=dst)

        fixed = apply_binary_fixup(target)
        assert len(fixed) == 2
        assert fixed[0] == AsmMovNode(
            start_position=4,
            source=src,
            destination=AsmRegisterNode(start_position=4, value="r10d"),
        )
        assert fixed[1] == AsmBinaryNode(
            start_position=4, operator=op, src=fixed[0].destination, dst=dst
        )

    def test_mul_unaffected(self):
        src = AsmImmediateIntNode(start_position=1, value=13)
        dst = AsmRegisterNode(start_position=2, value="r11d")
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
            source=dst,
            destination=AsmRegisterNode(start_position=4, value="r11d"),
        )
        assert fixed[1] == AsmBinaryNode(
            start_position=4,
            operator=AsmMultiply(start_position=3),
            src=src,
            dst=fixed[0].destination,
        )
        assert fixed[2] == AsmMovNode(
            start_position=4, source=fixed[0].destination, destination=dst
        )


class TestFunctionFixup:
    def test_simple(self):
        src = AsmStackNode(start_position=2, offset=-4)
        dst = AsmStackNode(start_position=3, offset=-8)
        target = AsmFunctionNode(
            start_position=0,
            identifier="abc",
            instructions=[AsmMovNode(start_position=1, source=src, destination=dst)],
            stack_size=8,
        )

        fixup_function_instructions(target)

        assert len(target.instructions) == 3
        i0 = target.instructions[0]
        assert i0 == AsmAllocateStackNode(start_position=0, stack_size=8)

        reg = AsmRegisterNode(start_position=1, value="r10d")
        i1 = target.instructions[1]
        assert i1 == AsmMovNode(start_position=1, source=src, destination=reg)

        i2 = target.instructions[2]
        assert i2 == AsmMovNode(start_position=1, source=reg, destination=dst)

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
        assert i0 == AsmAllocateStackNode(start_position=0, stack_size=8)

        reg = AsmRegisterNode(start_position=1, value="r10d")
        i1 = target.instructions[1]
        assert i1 == AsmMovNode(start_position=1, source=src, destination=reg)

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
        assert i0 == AsmAllocateStackNode(start_position=0, stack_size=8)

        reg = AsmRegisterNode(start_position=1, value="r10d")
        i1 = target.instructions[1]
        assert i1 == AsmMovNode(start_position=1, source=src, destination=reg)

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
        assert i0 == AsmAllocateStackNode(start_position=0, stack_size=8)

        reg = AsmRegisterNode(start_position=1, value="r11d")
        i1 = target.instructions[1]
        assert i1 == AsmMovNode(start_position=1, source=dst, destination=reg)

        i2 = target.instructions[2]
        assert i2 == AsmBinaryNode(
            start_position=1, operator=AsmMultiply(start_position=5), src=src, dst=reg
        )

        i3 = target.instructions[3]
        assert i3 == AsmMovNode(start_position=1, source=reg, destination=dst)


class TestProgramFixup:
    def test_simple(self):
        src = AsmStackNode(start_position=2, offset=-4)
        dst = AsmStackNode(start_position=3, offset=-8)
        func = AsmFunctionNode(
            start_position=0,
            identifier="abc",
            instructions=[AsmMovNode(start_position=1, source=src, destination=dst)],
            stack_size=8,
        )

        target = AsmProgramNode(start_position=0, function_definition=func)

        fixup_program_instructions(target)

        # Just check that the expected increase has happened
        assert len(target.function_definition.instructions) == 3

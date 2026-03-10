import pytest

from nqcc.codegen import (
    AsmAllocateStackNode,
    AsmFunctionNode,
    AsmMovNode,
    AsmOperandNode,
    AsmRegisterNode,
    AsmStackNode,
    apply_mov_fixup,
    fixup_function_instructions,
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

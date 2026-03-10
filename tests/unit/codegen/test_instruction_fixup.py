import pytest

from nqcc.codegen import apply_mov_fixup, AsmMovNode, AsmStackNode, AsmRegisterNode, AsmOperandNode


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

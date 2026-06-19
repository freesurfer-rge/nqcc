import pytest

from .utils import SAMPLE_PROGRAM_DIR, compile_run_check


class TestChapter10:
    SUB_DIR = "ch10"

    @pytest.mark.parametrize("v0", [0, 1, 5, 10])
    @pytest.mark.parametrize("v1", [0, 1, 3])
    def test_simple_call(self, v0: int, v1: int):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter10.SUB_DIR / "simple_static_var.c"
        assert target_file.exists(), f"{target_file} not found"

        macros = [f"V0={v0}", f"V1={v1}"]
        compile_run_check(target_file, macros=macros)

import pytest

from .utils import SAMPLE_PROGRAM_DIR, compile_run_check


class TestChapter04:
    SUB_DIR = "ch04"

    @pytest.mark.parametrize("v0", [0, 1, 11])
    def test_logical_not(self, v0: int):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter04.SUB_DIR / "return_logical_not.c"
        assert target_file.exists(), f"{target_file} not found"

        compile_run_check(target_file, macros=[f"V0={v0}"])
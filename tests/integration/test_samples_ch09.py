import pytest

from .utils import SAMPLE_PROGRAM_DIR, compile_run_check


class TestChapter09:
    SUB_DIR = "ch09"

    @pytest.mark.parametrize("v0", [1, 5, 15])
    def test_simple_while(self, v0: int):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter09.SUB_DIR / "simple_call.c"
        assert target_file.exists(), f"{target_file} not found"

        macros = [f"V0={v0}"]
        compile_run_check(target_file, macros=macros)

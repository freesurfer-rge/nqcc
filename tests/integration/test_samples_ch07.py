import pytest

from .utils import SAMPLE_PROGRAM_DIR, compile_run_check


class TestChapter07:
    SUB_DIR = "ch07"

    @pytest.mark.parametrize("v0", [0, 1, 2])
    def test_braced_if(self, v0: int):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter07.SUB_DIR / "braced_if.c"
        assert target_file.exists(), f"{target_file} not found"

        macros = [f"V0={v0}"]
        compile_run_check(target_file, macros=macros)

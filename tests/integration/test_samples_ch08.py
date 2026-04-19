import pytest

from .utils import SAMPLE_PROGRAM_DIR, compile_run_check


class TestChapter08:
    SUB_DIR = "ch08"

    @pytest.mark.parametrize("v0", [0, 1])
    @pytest.mark.parametrize("v1", [10, 20])
    @pytest.mark.parametrize("v2", [1, 2])
    def test_simple_while(self, v0: int, v1: int, v2: int):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter08.SUB_DIR / "simple_while.c"
        assert target_file.exists(), f"{target_file} not found"

        macros = [f"V0={v0}", f"V1={v1}", f"V2={v2}"]
        compile_run_check(target_file, macros=macros)
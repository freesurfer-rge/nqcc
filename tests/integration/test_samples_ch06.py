import pytest

from .utils import SAMPLE_PROGRAM_DIR, compile_run_check


class TestChapter06:
    SUB_DIR = "ch06"

    @pytest.mark.parametrize("v0", [0, 1])
    @pytest.mark.parametrize("v1", [0, 1, 5])
    def test_simple_ternay(self, v0: int, v1: int):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter06.SUB_DIR / "simple_ternary.c"
        assert target_file.exists(), f"{target_file} not found"

        macros = [f"V0={v0}", f"V1={v1}"]
        compile_run_check(target_file, macros=macros)

    @pytest.mark.parametrize("v0", [0, 4, 5, 10])
    @pytest.mark.parametrize("v1", [0, 1, 5, 40])
    @pytest.mark.parametrize("v2", [-10, 10])
    def test_simple_ternay(self, v0: int, v1: int, v2: int):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter06.SUB_DIR / "nested_if.c"
        assert target_file.exists(), f"{target_file} not found"

        macros = [f"V0={v0}", f"V1={v1}", f"V2={v2}"]
        compile_run_check(target_file, macros=macros)

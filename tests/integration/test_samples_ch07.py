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

    @pytest.mark.parametrize("v0", [1, 3, 7])
    @pytest.mark.parametrize("v1", [2, 5, 11])
    @pytest.mark.parametrize("v2", [1, 13, 17])
    def test_nested_scope(self, v0: int, v1: int, v2: int):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter07.SUB_DIR / "nested_scope.c"
        assert target_file.exists(), f"{target_file} not found"

        macros = [f"V0={v0}", f"V1={v1}", f"V2={v2}"]
        compile_run_check(target_file, macros=macros)

    @pytest.mark.parametrize("v0", [0, 1, 2])
    @pytest.mark.parametrize("v1", [0, 1, 2])
    @pytest.mark.parametrize("v2", [0, 1, 2])
    def test_deeply_nested_scope(self, v0: int, v1: int, v2: int):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter07.SUB_DIR / "deeply_nested_scope.c"
        assert target_file.exists(), f"{target_file} not found"

        macros = [f"V0={v0}", f"V1={v1}", f"V2={v2}"]
        compile_run_check(target_file, macros=macros)

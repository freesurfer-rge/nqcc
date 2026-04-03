import pytest

from .utils import SAMPLE_PROGRAM_DIR, compile_run_check


class TestChapter05:
    SUB_DIR = "ch05"

    @pytest.mark.parametrize(
        "op",
        ["+", "-", "*", "/", "%", "&", "|", "^", "<", "<=", "==", "!=", ">", ">=", "=", "&&", "||"],
    )
    def test_logical_compare(self, op: str):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter05.SUB_DIR / "simple_assign.c"
        assert target_file.exists(), f"{target_file} not found"

        macros = [f"OP={op}"]
        compile_run_check(target_file, macros=macros)

    @pytest.mark.parametrize("logical_op", ["||", "&&"])
    @pytest.mark.parametrize("v0", [0, 1])
    def test_short_circuit(self, logical_op: str, v0: int):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter05.SUB_DIR / "short_circuit_checker.c"
        assert target_file.exists(), f"{target_file} not found"

        macros = [f"LOGICAL_OP={logical_op}", f"V0={v0}"]
        compile_run_check(target_file, macros=macros)

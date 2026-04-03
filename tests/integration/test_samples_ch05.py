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

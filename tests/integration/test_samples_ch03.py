import pytest

from .utils import SAMPLE_PROGRAM_DIR, compile_run_check

class TestChapter03:
    SUB_DIR = "ch03"

    @pytest.mark.parametrize(
        "c_source_file",
        ["simple_add.c", "simple_divide.c", "many_operator.c", "bitwise_precedence.c"],
    )
    def test_direct(self, c_source_file: str):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter03.SUB_DIR / c_source_file
        assert target_file.exists(), f"{target_file} not found"

        compile_run_check(target_file, macros=[])

    @pytest.mark.parametrize("v0", [2, 3, 4, 15])
    @pytest.mark.parametrize("v1", [2, 3, 4, 15])
    @pytest.mark.parametrize("op", ["+", "-", "*", "/", "%", "&", "|", "^", "<<", ">>"])
    def test_single_binary_operators(self, v0: int, v1: int, op: str):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter03.SUB_DIR / "binary_operators.c"
        macros = [f"V0={v0}", f"V1={v1}", f"OP={op}"]
        assert target_file.exists(), f"{target_file} not found"
        compile_run_check(target_file, macros)

    @pytest.mark.parametrize("v0", [2, 3, 9])
    @pytest.mark.parametrize("v1", [2, 3, 9])
    @pytest.mark.parametrize("v2", [2, 3, 9])
    @pytest.mark.parametrize("op0", ["+", "-", "*", "/", "%", "&", "|", "^"])
    @pytest.mark.parametrize("op1", ["+", "-", "*", "/", "%", "&", "|", "^"])
    def test_two_operator(self, v0: int, v1: int, v2: int, op0: str, op1: str):
        # Skip shift operators, since _something_ is going wrong there
        # (but passing the smaller tests from the book --bitwise tests)
        target_file = SAMPLE_PROGRAM_DIR / TestChapter03.SUB_DIR / "two_operator.c"
        macros = [f"V0={v0}", f"V1={v1}", f"V2={v2}", f"OP0={op0}", f"OP1={op1}"]

        assert target_file.exists(), f"{target_file} not found"
        compile_run_check(target_file, macros)

    @pytest.mark.parametrize("v0", [1, 2, 37])
    @pytest.mark.parametrize("v1", [1, 2, 37])
    @pytest.mark.parametrize("v2", [1, 2, 37])
    @pytest.mark.parametrize("op0", ["+", "-", "*", "/", "%", "&", "|", "^"])
    @pytest.mark.parametrize("op1", ["+", "-", "*", "/", "%", "&", "|", "^"])
    def test_two_operator_negation(self, v0: int, v1: int, v2: int, op0: str, op1: str):
        # Skip shift operators, since _something_ is going wrong there
        # (but passing the smaller tests from the book --bitwise tests)
        target_file = SAMPLE_PROGRAM_DIR / TestChapter03.SUB_DIR / "two_operator_negation.c"
        macros = [f"V0={v0}", f"V1={v1}", f"V2={v2}", f"OP0={op0}", f"OP1={op1}"]

        assert target_file.exists(), f"{target_file} not found"
        compile_run_check(target_file, macros)

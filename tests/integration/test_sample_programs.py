import pathlib
import subprocess
import tempfile

import pytest

from nqcc import __main__ as compiler_driver

SAMPLE_PROGRAM_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "sample_programs"
assert SAMPLE_PROGRAM_DIR.exists(), f"{SAMPLE_PROGRAM_DIR=} not found!"


def _compile_run_check(target_file: pathlib.Path, macros: list[str]):
    with tempfile.TemporaryDirectory() as tmpdirname:
        working_dir = pathlib.Path(tmpdirname)
        executable_path = compiler_driver.main(
            target=target_file,
            working_dir=working_dir,
            exit_after_lex=False,
            exit_after_parse=False,
            exit_after_tacky=False,
            exit_after_codegen=False,
            preprocessor_defines=macros,
        )
        assert executable_path.exists(), f"Executable {executable_path} not generated!"
        result = subprocess.run([str(executable_path)], timeout=5)

        gcc_executable = "a.out"
        gcc_executable_path = working_dir / gcc_executable
        compile_cmd = ["gcc", "-o", str(gcc_executable_path), str(target_file)]
        for m in macros:
            compile_cmd.append("-D")
            compile_cmd.append(m)
        subprocess.run(compile_cmd, check=True, timeout=5)
        gcc_exec = subprocess.run([str(gcc_executable_path)], timeout=5)

        assert gcc_exec.returncode == result.returncode
    executable_path.unlink()


@pytest.mark.parametrize(
    "c_source_file",
    [
        "return_constant.c",
        "return_negative_constant.c",
        "return_bitwise_zero.c",
        "return_many_negatives.c",
    ],
)
def test_simple_return_values(
    c_source_file: str,
):
    target_file = SAMPLE_PROGRAM_DIR / c_source_file
    assert target_file.exists(), f"{target_file} not found"

    _compile_run_check(target_file, macros=[])


class TestChapter03:
    SUB_DIR = "ch03"

    @pytest.mark.parametrize(
        "c_source_file", ["simple_add.c", "simple_divide.c", "many_operator.c"]
    )
    def test_direct(self, c_source_file: str):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter03.SUB_DIR / c_source_file
        assert target_file.exists(), f"{target_file} not found"

        _compile_run_check(target_file, macros=[])

    @pytest.mark.parametrize("v0", [2, 3, 4, 127])
    @pytest.mark.parametrize("v1", [2, 3, 4, 127])
    @pytest.mark.parametrize("op", ["+", "-", "*", "/", "%", "&", "|", "^", "<<", ">>"])
    def test_single_binary_operators(self, v0: int, v1: int, op: str):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter03.SUB_DIR / "binary_operators.c"
        macros = [f"V0={v0}", f"V1={v1}", f"OP={op}"]
        assert target_file.exists(), f"{target_file} not found"
        _compile_run_check(target_file, macros)

    @pytest.mark.parametrize("v0", [2, 3, 31])
    @pytest.mark.parametrize("v1", [2, 3, 31])
    @pytest.mark.parametrize("v2", [2, 3, 31])
    @pytest.mark.parametrize("op0", ["+", "-", "*", "/", "%", "&", "|", "^", "<<", ">>"])
    @pytest.mark.parametrize("op1", ["+", "-", "*", "/", "%", "&", "|", "^", "<<", ">>"])
    def test_two_operator(self, v0: int, v1: int, v2: int, op0: str, op1: str):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter03.SUB_DIR / "two_operator.c"
        macros = [f"V0={v0}", f"V1={v1}", f"V2={v2}", f"OP0={op0}", f"OP1={op1}"]

        assert target_file.exists(), f"{target_file} not found"
        _compile_run_check(target_file, macros)

    @pytest.mark.parametrize("v0", [1, 2, 37])
    @pytest.mark.parametrize("v1", [1, 2, 37])
    @pytest.mark.parametrize("v2", [1, 2, 37])
    @pytest.mark.parametrize("op0", ["+", "-", "*", "/", "%", "&", "|", "^", "<<", ">>"])
    @pytest.mark.parametrize("op1", ["+", "-", "*", "/", "%", "&", "|", "^", "<<", ">>"])
    def test_two_operator_negation(self, v0: int, v1: int, v2: int, op0: str, op1: str):
        target_file = SAMPLE_PROGRAM_DIR / TestChapter03.SUB_DIR / "two_operator_negation.c"
        macros = [f"V0={v0}", f"V1={v1}", f"V2={v2}", f"OP0={op0}", f"OP1={op1}"]

        assert target_file.exists(), f"{target_file} not found"
        _compile_run_check(target_file, macros)

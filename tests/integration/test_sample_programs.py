import pathlib
import subprocess
import tempfile

import pytest

from nqcc import __main__ as compiler_driver

SAMPLE_PROGRAM_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "sample_programs"
assert SAMPLE_PROGRAM_DIR.exists(), f"{SAMPLE_PROGRAM_DIR=} not found!"


def _compile_run_check(target_file: pathlib.Path, expected_return: int):
    with tempfile.TemporaryDirectory() as tmpdirname:
        working_dir = pathlib.Path(tmpdirname)
        executable_path = compiler_driver.main(
            target=target_file,
            working_dir=working_dir,
            exit_after_lex=False,
            exit_after_parse=False,
            exit_after_tacky=False,
            exit_after_codegen=False,
        )
        assert executable_path.exists(), f"Executable {executable_path} not generated!"
        result = subprocess.run([str(executable_path)], timeout=5)

        gcc_executable = "a.out"
        gcc_executable_path = working_dir / gcc_executable
        compile_cmd = ["gcc", "-o", str(gcc_executable_path), str(target_file)]
        subprocess.run(compile_cmd, check=True, timeout=5)

        gcc_exec = subprocess.run([str(gcc_executable_path)], timeout=5)
        assert gcc_exec.returncode == result.returncode

        assert result.returncode == expected_return
    executable_path.unlink()


@pytest.mark.parametrize(
    ["c_source_file", "expected_return"],
    [
        ("return_constant.c", 2),
        ("return_negative_constant.c", 246),
        ("return_bitwise_zero.c", 255),
        ("return_many_negatives.c", 10),
    ],
)
def test_return_constant(c_source_file: str, expected_return: int):
    target_file = SAMPLE_PROGRAM_DIR / c_source_file
    assert target_file.exists(), f"{target_file} not found"

    _compile_run_check(target_file, expected_return)

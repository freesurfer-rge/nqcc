import pathlib
import subprocess
import tempfile

from nqcc import __main__ as compiler_driver

SAMPLE_PROGRAM_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "sample_programs"
assert SAMPLE_PROGRAM_DIR.exists(), f"{SAMPLE_PROGRAM_DIR=} not found!"


def test_return_constant():
    target_file = SAMPLE_PROGRAM_DIR / "return_constant.c"

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
        assert result.returncode == 2
    executable_path.unlink()

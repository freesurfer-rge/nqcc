import pathlib
import subprocess
import tempfile

from nqcc import __main__ as compiler_driver

SAMPLE_PROGRAM_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "sample_programs"
assert SAMPLE_PROGRAM_DIR.exists(), f"{SAMPLE_PROGRAM_DIR=} not found!"


def compile_run_check(target_file: pathlib.Path, macros: list[str]):
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

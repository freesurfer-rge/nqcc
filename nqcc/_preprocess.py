import pathlib
import subprocess

PREPROCESS_EXTENSION = ".i"


def preprocess_c_file(target_path: pathlib.Path, working_dir: pathlib.Path) -> pathlib.Path:
    assert target_path.exists(), f"{target_path} not found"
    assert working_dir.exists(), f"{working_dir} not found"

    output_file_name = target_path.name + PREPROCESS_EXTENSION
    output_path = working_dir / output_file_name

    preprocess_command = ["gcc", "-E", "-P", target_path, "-o", output_path]
    subprocess.run(preprocess_command, check=True, timeout=5)

    return output_path

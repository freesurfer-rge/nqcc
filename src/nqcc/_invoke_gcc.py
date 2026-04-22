import pathlib
import subprocess

PREPROCESS_EXTENSION = ".i"


def preprocess_c_file(
    target_path: pathlib.Path, working_dir: pathlib.Path, macro_defines: list[str]
) -> pathlib.Path:
    assert target_path.exists(), f"{target_path} not found"
    assert working_dir.exists(), f"{working_dir} not found"

    output_file_name = target_path.stem + PREPROCESS_EXTENSION
    output_path = working_dir / output_file_name

    preprocess_command = ["gcc", "-E", "-P", str(target_path), "-o", str(output_path)]
    for macro in macro_defines:
        preprocess_command.append("-D")
        preprocess_command.append(macro)
    subprocess.run(preprocess_command, check=True, timeout=5)

    return output_path


def generate_objectfile(assembly_path: pathlib.Path, output_path: pathlib.Path) -> pathlib.Path:
    assert assembly_path.exists(), f"{assembly_path} not found"

    generation_command = ["gcc", "-c", str(assembly_path), "-o", str(output_path)]
    subprocess.run(generation_command)

    return output_path

def generate_executable(assembly_path: pathlib.Path, output_path: pathlib.Path) -> pathlib.Path:
    assert assembly_path.exists(), f"{assembly_path} not found"

    generation_command = ["gcc", str(assembly_path), "-o", str(output_path)]
    subprocess.run(generation_command)

    return output_path

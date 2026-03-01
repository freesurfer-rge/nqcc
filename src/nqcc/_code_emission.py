import pathlib

from nqcc.codegen import AsmProgramNode

ASSEMBLY_EXTENSION = ".s"

def emit_assembler(
    asm_ast: AsmProgramNode, *, working_dir: pathlib.Path, file_stem: str
) -> pathlib.Path:
    assert working_dir.exists(), f"Unable to find working directory {working_dir}"

    asm_lines = asm_ast.emit_instructions()

    output_file = file_stem + ASSEMBLY_EXTENSION
    output_path = working_dir / output_file
    with open(output_path, "w") as of:
        for l in asm_lines:
            of.write(l + "\n")

    return output_path
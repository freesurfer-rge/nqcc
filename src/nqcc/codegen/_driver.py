import pathlib

from nqcc.codegen import AsmProgramNode, convert_tacky_program
from nqcc.tacky import TackyProgramNode

ASM_AST_EXTENSION = ".asm_ast"


def codegen_driver(
    source_ast: TackyProgramNode, *, working_dir: pathlib.Path, file_stem: str
) -> AsmProgramNode:
    assert working_dir.exists(), f"Unable to find working directory {working_dir}"

    asm_ast_0 = convert_tacky_program(source_ast)

    output_file = file_stem + ".0" + ASM_AST_EXTENSION
    output_path = working_dir / output_file
    with open(output_path, "w") as of:
        of.write(asm_ast_0.model_dump_json(indent=4, round_trip=True))

    return asm_ast_0

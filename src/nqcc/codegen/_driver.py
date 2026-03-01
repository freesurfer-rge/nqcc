import pathlib

from nqcc.codegen import AsmProgramNode, convert_program_node
from nqcc.parser import SourceProgramNode

ASM_AST_EXTENSION = ".asm_ast"


def codegen_driver(
    source_ast: SourceProgramNode, *, working_dir: pathlib.Path, file_stem: str
) -> AsmProgramNode:
    assert working_dir.exists(), f"Unable to find working directory {working_dir}"

    asm_ast = convert_program_node(source_ast)

    output_file = file_stem + ASM_AST_EXTENSION
    output_path = working_dir / output_file
    with open(output_path, "w") as of:
        of.write(asm_ast.model_dump_json(indent=4, round_trip=True))

    return asm_ast

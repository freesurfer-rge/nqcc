import pathlib

from nqcc.tacky import TackyProgramNode

from ._assembler_ast import AsmProgramNode
from ._convert_tacky import convert_tacky_program
from ._pseudo_replace import PseudoRegisterReplacer

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

    prr = PseudoRegisterReplacer()
    prr.pseudo_replace(asm_ast_0)

    output_file = file_stem + ".1" + ASM_AST_EXTENSION
    output_path = working_dir / output_file
    with open(output_path, "w") as of:
        of.write(asm_ast_0.model_dump_json(indent=4, round_trip=True))

    return asm_ast_0

import pathlib

from nqcc.frontend.parser import SourceProgramNode
from nqcc.frontend.semantic_analysis import SymbolTable

from ._tacky_ast import TackyProgramNode
from ._tacky_generator import TackyGenerator

TACKY_FILE = "tacky.ast"


def tacky_driver(
    source_program: SourceProgramNode, symbol_table: SymbolTable, *, working_dir: pathlib.Path
) -> TackyProgramNode:
    assert working_dir.exists(), f"Unable to find working directory {working_dir}"

    generator = TackyGenerator()
    tacky_ast = generator.emit_program(source_program, symbol_table)

    output_path = working_dir / TACKY_FILE
    with open(output_path, "w") as of:
        of.write(tacky_ast.model_dump_json(indent=4, round_trip=True))

    return tacky_ast

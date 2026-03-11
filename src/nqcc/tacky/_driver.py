import pathlib

from nqcc.parser import SourceProgramNode

from ._tacky_ast import TackyProgramNode
from ._tacky_generator import TackyGenerator

TACKY_FILE = "tacky.ast"


def tacky_driver(
    source_program: SourceProgramNode, *, working_dir: pathlib.Path
) -> TackyProgramNode:
    assert working_dir.exists(), f"Unable to find working directory {working_dir}"

    generator = TackyGenerator()
    tacky_ast = generator.emit_program(source_program)

    output_path = working_dir / TACKY_FILE
    with open(output_path, "w") as of:
        of.write(tacky_ast.model_dump_json(indent=4, round_trip=True))

    return tacky_ast

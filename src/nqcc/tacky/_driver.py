import pathlib

from nqcc.parser import SourceProgramNode

from ._tacky_ast import TackyProgramNode
from ._tacky_generator import TackyGenerator

SOURCE_TACKY_EXTENSION = ".tacky_ast"


def tacky_driver(
    source_program: SourceProgramNode, *, working_dir: pathlib.Path, file_stem: str
) -> TackyProgramNode:
    assert working_dir.exists(), f"Unable to find working directory {working_dir}"

    generator = TackyGenerator()
    tacky_ast = generator.emit_program(source_program)

    output_file = file_stem + SOURCE_TACKY_EXTENSION
    output_path = working_dir / output_file
    with open(output_path, "w") as of:
        of.write(tacky_ast.model_dump_json(indent=4, round_trip=True))

    return tacky_ast

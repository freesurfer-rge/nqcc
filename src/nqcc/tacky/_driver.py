import pathlib

from nqcc.parser import SourceProgramNode

from ._tacky_ast import TackyProgramNode

SOURCE_AST_EXTENSION = ".tacky_ast"


def tacky_driver(
    source_program: SourceProgramNode, *, working_dir: pathlib.Path, file_stem: str
) -> TackyProgramNode:
    assert working_dir.exists(), f"Unable to find working directory {working_dir}"
    raise NotImplementedError("TBD")

import pathlib

from nqcc.parser import SourceProgramNode

def semantic_analysis_driver(
    source_program: SourceProgramNode, *, working_dir: pathlib.Path
) -> SourceProgramNode:
    assert working_dir.exists(), f"Unable to find working directory {working_dir}"

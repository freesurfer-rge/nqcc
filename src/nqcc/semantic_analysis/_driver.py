import pathlib

from nqcc.parser import SourceProgramNode

from ._loop_labelling import label_loops_program
from ._identifier_resolution import resolve_program

SEMANTIC_ANALYSIS_RESOLVED_FILE = "semantic-analysis.0.ast"

SEMANTIC_ANALYSIS_LABELLED_LOOPS_FILE = "semantic-analysis.1.ast"


def semantic_analysis_driver(
    source_program: SourceProgramNode, *, working_dir: pathlib.Path
) -> SourceProgramNode:
    assert working_dir.exists(), f"Unable to find working directory {working_dir}"

    # Resolve variables
    resolved_program = resolve_program(source_program)

    output_path = working_dir / SEMANTIC_ANALYSIS_RESOLVED_FILE
    with open(output_path, "w") as of:
        of.write(resolved_program.model_dump_json(indent=4))

    # Label loops (in place)
    label_loops_program(resolved_program)

    output_path = working_dir / SEMANTIC_ANALYSIS_LABELLED_LOOPS_FILE
    with open(output_path, "w") as of:
        of.write(resolved_program.model_dump_json(indent=4))

    return resolved_program

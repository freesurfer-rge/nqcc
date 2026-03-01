import pathlib

from nqcc.lexer import TokenItem

from ._source_ast import parse_program
from ._token_tape import TokenTape

SOURCE_AST_EXTENSION = ".source_ast"

def parser_driver(tokens: list[TokenItem], *, working_dir: pathlib.Path, file_stem: str):
    # TODO: Figure out return type
    assert working_dir.exists(), f"Unable to find working directory {working_dir}"
    tt = TokenTape(tokens)

    source_ast = parse_program(tt)

    output_file = file_stem + SOURCE_AST_EXTENSION
    output_path = working_dir / output_file
    with open(output_path, "w") as of:
        of.write(source_ast.model_dump_json(indent=4, round_trip=True))
import pathlib

from nqcc.lexer import Token

from ._source_ast import SourceProgramNode, parse_program
from ._token_tape import TokenTape

SOURCE_AST_FILE = "source.ast"


def parser_driver(tokens: list[Token], *, working_dir: pathlib.Path) -> SourceProgramNode:
    assert working_dir.exists(), f"Unable to find working directory {working_dir}"
    tt = TokenTape(tokens)

    source_ast = parse_program(tt)

    output_path = working_dir / SOURCE_AST_FILE
    with open(output_path, "w") as of:
        of.write(source_ast.model_dump_json(indent=4))

    return source_ast

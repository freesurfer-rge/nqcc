from enum import StrEnum
import json
import pathlib

from nqcc.frontend.lexer import Token, lex_string
from nqcc.frontend.parser import SourceProgramNode, TokenTape, parse_program

SOURCE_AST_FILE = "source.ast"
TOKEN_FILE = "lexer.tokens"

class Stage(StrEnum):
    LEXER = 'lexer'
    PARSER = 'parser'
    SEMANTIC_ANALYSIS = "semantic_analysis"
    TACKY = 'tacky'

class FrontEnd:
    def __init__(self, working_dir: pathlib.Path | None):
        self._working_dir : pathlib.Path | None
        if working_dir and working_dir.exists() and working_dir.is_dir():
            self._working_dir = working_dir
        self._c_source: str = ""
        self._token_list: list[Token] = []
        self._source_ast: SourceProgramNode | None = None


    def run_lexer(self):
        self._token_list = lex_string(self.c_source)

        if self._working_dir:
            output_path = self._working_dir / TOKEN_FILE
            with open(output_path, "w") as token_file:
                json.dump([t.model_dump(round_trip=True) for t in self.tokens], token_file, indent=4)

    def run_parser(self):
        tt = TokenTape(self.tokens)
                       
        self._source_ast = parse_program(tt)

        if self._working_dir:
            output_path = self._working_dir / SOURCE_AST_FILE
            with open(output_path, "w") as of:
                of.write(self.source_ast.model_dump_json(indent=4))

    @property
    def c_source(self) -> str:
        return self._c_source

    @property
    def tokens(self) -> list[Token]:
        return self._token_list
    
    @property
    def source_ast(self) -> SourceProgramNode:
        if not self._source_ast:
            raise ValueError("Parser not yet run")
        return self._source_ast
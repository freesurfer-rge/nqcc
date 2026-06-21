import json
import pathlib

from nqcc.frontend.lexer import Token, lex_string
from nqcc.frontend.parser import SourceProgramNode, TokenTape, parse_program
from nqcc.frontend.semantic_analysis import SymbolTable, label_loops_program, resolve_program
from nqcc.frontend.tacky import TackyGenerator, TackyProgramNode

SEMANTIC_ANALYSIS_RESOLVED_FILE = "semantic-analysis.0.ast"
SEMANTIC_ANALYSIS_LABELLED_LOOPS_FILE = "semantic-analysis.1.ast"
SEMANTIC_ANALYSIS_SYMBOL_FILE = "semantic-analysis.symbols"
SOURCE_AST_FILE = "source.ast"
TACKY_FILE = "tacky.ast"
TOKEN_FILE = "lexer.tokens"


class FrontEnd:
    def __init__(self, c_source: str, *, working_dir: pathlib.Path | None):
        self._working_dir: pathlib.Path | None
        if working_dir and working_dir.exists() and working_dir.is_dir():
            self._working_dir = working_dir
        self._c_source: str = c_source
        self._token_list: list[Token] = []
        self._source_ast: SourceProgramNode | None = None
        self._symbol_table: SymbolTable | None = None
        self._tacky: TackyProgramNode | None = None

    def run_lexer(self):
        self._token_list = lex_string(self.c_source)

        if self._working_dir:
            output_path = self._working_dir / TOKEN_FILE
            with open(output_path, "w") as token_file:
                json.dump(
                    [t.model_dump(round_trip=True) for t in self.tokens], token_file, indent=4
                )

    def run_parser(self):
        tt = TokenTape(self.tokens)

        self._source_ast = parse_program(tt)

        if self._working_dir:
            output_path = self._working_dir / SOURCE_AST_FILE
            with open(output_path, "w") as of:
                of.write(self.source_ast.model_dump_json(indent=4))

    def run_semantic_analysis(self):
        # Resolve variables
        self._source_ast = resolve_program(self.source_ast)

        if self._working_dir:
            output_path = self._working_dir / SEMANTIC_ANALYSIS_RESOLVED_FILE
            with open(output_path, "w") as of:
                of.write(self._source_ast.model_dump_json(indent=4))

        # Label loops (in place)
        label_loops_program(self._source_ast)

        if self._working_dir:
            output_path = self._working_dir / SEMANTIC_ANALYSIS_LABELLED_LOOPS_FILE
            with open(output_path, "w") as of:
                of.write(self._source_ast.model_dump_json(indent=4))

        # Check symbols
        self._symbol_table = SymbolTable()
        self._symbol_table.check_program(self._source_ast)

        if self._working_dir:
            output_path = self._working_dir / SEMANTIC_ANALYSIS_SYMBOL_FILE
            with open(output_path, "w") as of:
                of.write(self._symbol_table.model_dump_json(indent=4))

    def run_tacky_generation(self):
        generator = TackyGenerator()
        self._tacky = generator.emit_program(self.source_ast, self.symbol_table)

        if self._working_dir:
            output_path = self._working_dir / TACKY_FILE
            with open(output_path, "w") as of:
                of.write(self._tacky.model_dump_json(indent=4, round_trip=True))

    @property
    def c_source(self) -> str:
        return self._c_source

    @property
    def tokens(self) -> list[Token]:
        return self._token_list

    @property
    def source_ast(self) -> SourceProgramNode:
        if not self._source_ast:
            raise ValueError("Parser not run")
        return self._source_ast

    @property
    def symbol_table(self) -> SymbolTable:
        if not self._symbol_table:
            raise ValueError("Semantic analysis not run")
        return self._symbol_table

    @property
    def tacky(self) -> TackyProgramNode:
        if not self._tacky:
            raise ValueError("Tacky Generation not run")
        return self._tacky

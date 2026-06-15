import logging
import pathlib

from nqcc.semantic_analysis import SymbolTable
from nqcc.tacky import TackyProgramNode

from ._assembler_ast import AsmProgramNode
from ._convert_tacky import convert_tacky_program
from ._instruction_fixup import fixup_program_instructions
from ._pseudo_replace import PseudoRegisterReplacer

CONVERTED_FILE = "asm.0.ast"
PSEUDOREG_REPLACE_FILE = "asm.1.ast"
FIXUP_FILE = "asm.2.ast"

_logger = logging.getLogger("nqcc")


def _write_output(asm_prog: AsmProgramNode, output_path: pathlib.Path) -> None:
    with open(output_path, "w") as of:
        of.write(asm_prog.model_dump_json(indent=4))


def codegen_driver(source_ast: TackyProgramNode, symbol_table: SymbolTable, *, working_dir: pathlib.Path) -> AsmProgramNode:
    assert working_dir.exists(), f"Unable to find working directory {working_dir}"

    _logger.info("Converting from Tacky")
    asm_ast_0 = convert_tacky_program(source_ast)
    _write_output(asm_ast_0, working_dir / CONVERTED_FILE)

    _logger.info("Running Pseudoregister replacement")
    prr = PseudoRegisterReplacer(symbol_table)
    prr.pseudo_replace(asm_ast_0)
    _write_output(asm_ast_0, working_dir / PSEUDOREG_REPLACE_FILE)

    _logger.info("Fixing up instructions")
    fixup_program_instructions(asm_ast_0)
    _write_output(asm_ast_0, working_dir / FIXUP_FILE)

    return asm_ast_0

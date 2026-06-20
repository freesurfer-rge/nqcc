import argparse
import logging
import pathlib
import shutil

from nqcc import emit_assembler, generate_executable, generate_objectfile, preprocess_c_file
from nqcc.codegen import codegen_driver
from nqcc.frontend.lexer import lexer_driver
from nqcc.frontend.parser import parser_driver
from nqcc.semantic_analysis import semantic_analysis_driver
from nqcc.tacky import tacky_driver

_DESC = """\
An implementation of the C Compiler described in Nora 
Sandler's book "Writing a C Compiler."

The preprocessor will always be run.
"""

_DEFAULT_WORKING_DIR = "temp-nqcc"

_WORKING_DIR_DESC = f"""\
Directory to store intermediate files. By default
this will be '{_DEFAULT_WORKING_DIR}' in the same
directory as the target file. This directory will
be DELETED and recreated before any other tooling
runs.
"""

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger("nqcc")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="nqcc",
        description=_DESC,
        add_help=True,
    )

    book_group = parser.add_argument_group(title="Required for book's test suite")

    book_group.add_argument("-c", action="store_true", help="Compile only", dest="compile_only")

    exit_group = book_group.add_mutually_exclusive_group()
    exit_group.add_argument("--lex", action="store_true", help="Exit after the lexer")
    exit_group.add_argument("--parse", action="store_true", help="Exit after the parser")
    exit_group.add_argument("--validate", action="store_true", help="Exit after semantic analysis")
    exit_group.add_argument("--tacky", action="store_true", help="Exit after tacky generation")
    exit_group.add_argument(
        "--codegen",
        action="store_true",
        help="Exit after code generation",
    )

    preprocessor_group = parser.add_argument_group(title="Preprocessor arguments")
    preprocessor_group.add_argument(
        "-D",
        action="append",
        dest="define_list",
        default=[],
        help="Preprocessor macros (-D NAME or -D NAME=VALUE)."
        + " Repeat as many -D values as necessary",
    )

    parser.add_argument("--working-dir", type=pathlib.Path, required=False, help=_WORKING_DIR_DESC)
    parser.add_argument("target", type=pathlib.Path, help="Path to target C file")

    args = parser.parse_args()

    if not args.working_dir:
        args.working_dir = args.target.parent / _DEFAULT_WORKING_DIR

    return args


def main(
    *,
    target: pathlib.Path,
    working_dir: pathlib.Path,
    exit_after_lex: bool,
    exit_after_parse: bool,
    exit_after_semantic_analysis: bool,
    exit_after_tacky: bool,
    exit_after_codegen: bool,
    compile_only: bool,
    preprocessor_defines: list[str],
):

    assert target.exists(), f"Target {target} does not exist!"

    if working_dir.exists():
        _logger.warning("Deleting working directory %s", working_dir)
        shutil.rmtree(working_dir)
    working_dir.mkdir()

    _logger.info("Running preprocessor")
    preprocessed_file_path = preprocess_c_file(
        target, working_dir, macro_defines=preprocessor_defines
    )

    _logger.info("Running lexer")
    all_tokens = lexer_driver(preprocessed_file_path)

    if exit_after_lex:
        _logger.info("Exiting after lexer")
        return

    file_stem = target.stem

    _logger.info("Running parser")
    src_ast = parser_driver(all_tokens, working_dir=working_dir)

    if exit_after_parse:
        _logger.info("Exiting after parse")
        return

    _logger.info("Running semantic analysis")
    src_ast, symbol_table = semantic_analysis_driver(src_ast, working_dir=working_dir)

    if exit_after_semantic_analysis:
        _logger.info("Exiting after semantic analysis")
        return

    _logger.info("Running tacking generation")
    tacky_ast = tacky_driver(src_ast, symbol_table, working_dir=working_dir)

    if exit_after_tacky:
        _logger.info("Exiting after tacky generation")
        return

    _logger.info("Running code generator")
    asm_ast = codegen_driver(tacky_ast, symbol_table, working_dir=working_dir)

    if exit_after_codegen:
        _logger.info("Exiting after code generation")
        return

    _logger.info("Emitting assembly code")
    asm_path = emit_assembler(asm_ast, symbol_table, working_dir=working_dir, file_stem=file_stem)

    if compile_only:
        _logger.info("Generating object file")
        final_output_path = generate_objectfile(asm_path, target.parent / f"{file_stem}.o")
    else:
        _logger.info("Generating executable")
        final_output_path = generate_executable(asm_path, target.parent / file_stem)
    _logger.info("Done")
    return final_output_path


if __name__ == "__main__":
    args = parse_args()

    _ = main(
        target=args.target,
        working_dir=args.working_dir,
        exit_after_lex=args.lex,
        exit_after_parse=args.parse,
        exit_after_semantic_analysis=args.validate,
        exit_after_tacky=args.tacky,
        exit_after_codegen=args.codegen,
        compile_only=args.compile_only,
        preprocessor_defines=args.define_list,
    )

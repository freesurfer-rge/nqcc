import argparse
import logging
import pathlib
import shutil

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
    book_group.add_argument("--lex", action="store_true", help="Only run the lexer then exit")
    book_group.add_argument(
        "--parse", action="store_true", help="Only run the parser then exit (implies --lex)"
    )
    book_group.add_argument(
        "--codegen",
        action="store_true",
        help="Only run the code generator then exit (implies --lex and --parse)",
    )

    parser.add_argument("--working-dir", type=pathlib.Path, required=False, help=_WORKING_DIR_DESC)
    parser.add_argument("target", type=pathlib.Path, help="Path to target C file")

    args = parser.parse_args()

    if args.codegen:
        args.parse = True
    if args.parse:
        args.lex = True

    if not args.working_dir:
        args.working_dir = args.target.parent / _DEFAULT_WORKING_DIR

    return args


def main():
    args = parse_args()

    assert args.target.exists(), f"Target {args.target} does not exist!"

    if args.working_dir.exists():
        _logger.warning(f"Deleting working directory {args.working_dir}")
        shutil.rmtree(args.working_dir)
    args.working_dir.mkdir()


if __name__ == "__main__":
    main()

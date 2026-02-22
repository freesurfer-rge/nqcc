import argparse
import pathlib


def parse_args():
    parser = argparse.ArgumentParser(
        prog="nqcc",
        description="An implementation of the C Compiler described in Nora Sandler's book Writing a C Compiler",
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

    parser.add_argument("target", type=pathlib.Path, help="Path to target C file")

    args = parser.parse_args()

    if args.codegen:
        args.parse = True
    if args.parse:
        args.lex = True

    return args


def main():
    args = parse_args()


if __name__ == "__main__":
    main()

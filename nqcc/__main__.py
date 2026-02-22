import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        prog="nqcc",
        description="An implementation of the C Compiler described in Nora Sandler's book Writing a C Compiler",
        add_help=True,
    )

    parser.add_argument("--lex", action="store_true", help="Only run the lexer then exit")

    parser.add_argument(
        "--parse", action="store_true", help="Only run the parser then exit (implies --lex)"
    )

    args = parser.parse_args()

    if args.parse:
        args.lex = True

    return args


def main():
    args = parse_args()


if __name__ == "__main__":
    main()

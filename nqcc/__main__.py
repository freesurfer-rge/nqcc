import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        prog = "nqcc",
        description = "An implementation of the C Compiler described in Nora Sandler's book Writing a C Compiler",
        add_help=True
    )

    args = parser.parse_args()
    return args

def main():
    args = parse_args()

if __name__ == "__main__":
    main()
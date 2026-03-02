import json
import pathlib

from ._lexer import lex_string
from ._tokens import Token

TOKEN_EXTENSION = ".tokens"


def lexer_driver(preprocessed_file: pathlib.Path) -> list[Token]:
    assert preprocessed_file.exists(), f"Preprocessed file {preprocessed_file} not found!"

    with open(preprocessed_file, "r") as f:
        c_source = f.read()

    token_list = lex_string(c_source)

    output_file = preprocessed_file.stem + TOKEN_EXTENSION
    output_path = preprocessed_file.parent / output_file
    with open(output_path, "w") as token_file:
        json.dump([t.model_dump(round_trip=True) for t in token_list], token_file, indent=4)

    return token_list

import json
import pathlib

from ._lexer import Lexer
from ._tokens import TokenItem

TOKEN_EXTENSION = ".tokens"


def lexer_driver(preprocessed_file: pathlib.Path) -> list[TokenItem]:
    assert preprocessed_file.exists(), f"Preprocessed file {preprocessed_file} not found!"

    lexer = Lexer()

    with open(preprocessed_file, "r") as f:
        while True:
            ch = f.read(1)
            if not ch:
                break
            lexer.push_character(ch)
    lexer.character_stream_done()

    token_list = lexer.completed_token_list

    output_file = preprocessed_file.stem + TOKEN_EXTENSION
    output_path = preprocessed_file.parent / output_file
    with open(output_path, "w") as token_file:
        json.dump([t.model_dump(round_trip=True) for t in token_list], token_file, indent=4)

    return token_list

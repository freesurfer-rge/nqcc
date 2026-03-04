from nqcc.lexer import Token


class SourceASTBadTypeError(ValueError):
    def __init__(
        self, *, expected_type: type | tuple[type, ...], actual_token: Token, message: str
    ):
        self.expected_type = expected_type
        self.actual_token = actual_token
        self.message = message
        super().__init__(self.message)


class SourceASTBadValueError(ValueError):
    def __init__(self, *, expected_value: str, actual_token: Token, message: str):
        self.expected_value = expected_value
        self.actual_token = actual_token
        self.message = message
        super().__init__(self.message)

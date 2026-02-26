from nqcc.lexer import TokenItem


class SourceASTError(ValueError):
    def __init__(self, *, expected_type: type, actual_token: TokenItem, message: str):
        self.expected_type = expected_type
        self.actual_token = actual_token
        self.message = message
        super().__init__(self.message)

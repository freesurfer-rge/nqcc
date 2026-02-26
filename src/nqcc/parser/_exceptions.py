from nqcc.lexer import TokenItem


class SourceASTBadTypeError(ValueError):
    def __init__(self, *, expected_type: type, actual_token: TokenItem, message: str):
        self.expected_type = expected_type
        self.actual_token = actual_token
        self.message = message
        super().__init__(self.message)

class SourceASTBadValueError(ValueError):
    def __init__(self, *, expected_value: str, actual_token: TokenItem, message: str):
        self.expected_value = expected_value
        self.actual_token = actual_token
        self.message = message
        super().__init__(self.message)

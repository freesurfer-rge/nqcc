from typing import Union

from pydantic import BaseModel


class VariableInt:
    pass


VariableType = Union[VariableInt]


class FunctionType(BaseModel):
    param_count: int
    defined: bool


SymbolType = Union[VariableType, FunctionType]


class SymbolTable:
    def __init__(self) -> None:
        self.symbol_table: dict[str, SymbolType] = {}

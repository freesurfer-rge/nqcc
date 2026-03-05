from typing import Literal, Union

from pydantic import BaseModel


class TackyASTNode(BaseModel):
    node_type: str
    start_position: int


class TackyConstantIntNode(TackyASTNode):
    node_type: Literal["TackyConstantIntNode"] = "TackyConstantIntNode"
    value: int


class TackyVarNode(TackyASTNode):
    node_type: Literal["TackyVarNode"] = "TackyVarNode"
    identifier: str

TackyValue = Union[TackyConstantIntNode, TackyVarNode]

class TackyComplementNode(TackyASTNode):
    node_type: Literal["TackyComplementNode"] = "TackyComplementNode"


class TackyNegateNode(TackyASTNode):
    node_type: Literal["TackyNegateNode"] = "TackyNegateNode"


TackyUnaryOperator = Union[TackyComplementNode, TackyNegateNode]


class TackyReturnNode(TackyASTNode):
    node_type: Literal["TackyReturnNode"] = "TackyReturnNode"
    value: TackyValue

class TackyUnaryNode(TackyASTNode):
    node_type: Literal["TackUnaryNode"] = "TackUnaryNode"
    operator: TackyUnaryOperator
    src: TackyValue
    dst: TackyValue

TackyInstruction = Union[TackyReturnNode, TackyUnaryNode]

class TackyFunctionNode(TackyASTNode):
    node_type: Literal["TackyFunctionNode"] = "TackyFunctionNode"
    identifier: str
    instructions: list[TackyInstruction]

class TackyProgramNode(TackyASTNode):
    node_type: Literal["TackyProgramNode"] = "TackyProgramNode"
    identifier: str
    function_definition: TackyFunctionNode
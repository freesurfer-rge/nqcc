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


class TackyAdd(TackyASTNode):
    node_type: Literal["TackyAdd"] = "TackyAdd"


class TackySubtract(TackyASTNode):
    node_type: Literal["TackySubtract"] = "TackySubtract"


class TackyMultiply(TackyASTNode):
    node_type: Literal["TackyMultiply"] = "TackyMultiply"


class TackyDivide(TackyASTNode):
    node_type: Literal["TackyDivide"] = "TackyDivide"


class TackyModulo(TackyASTNode):
    node_type: Literal["TackyModulo"] = "TackyModulo"


TackyBinaryOperator = Union[TackyAdd, TackySubtract, TackyMultiply, TackyDivide, TackyModulo]


class TackyReturnNode(TackyASTNode):
    node_type: Literal["TackyReturnNode"] = "TackyReturnNode"
    value: TackyValue


class TackyUnaryNode(TackyASTNode):
    node_type: Literal["TackUnaryNode"] = "TackUnaryNode"
    operator: TackyUnaryOperator
    src: TackyValue
    dst: TackyValue


class TackyBinaryNode(TackyASTNode):
    node_type: Literal["TackyBinaryNode"] = "TackyBinaryNode"
    operator: TackyBinaryOperator
    left: TackyValue
    right: TackyValue
    dst: TackyValue


TackyInstruction = Union[TackyReturnNode, TackyUnaryNode, TackyBinaryNode]


class TackyFunctionNode(TackyASTNode):
    node_type: Literal["TackyFunctionNode"] = "TackyFunctionNode"
    identifier: str
    instructions: list[TackyInstruction]


class TackyProgramNode(TackyASTNode):
    node_type: Literal["TackyProgramNode"] = "TackyProgramNode"
    function_definition: TackyFunctionNode

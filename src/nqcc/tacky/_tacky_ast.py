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


class TackyComplement(TackyASTNode):
    node_type: Literal["TackyComplement"] = "TackyComplement"


class TackyNegate(TackyASTNode):
    node_type: Literal["TackyNegate"] = "TackyNegate"

class TackyLogicalNot(TackyASTNode):
    node_type: Literal["TackyLogicalNot"] = "TackyLogicalNot"


TackyUnaryOperator = Union[TackyComplement, TackyNegate, TackyLogicalNot]


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


class TackyBitwiseAnd(TackyASTNode):
    node_type: Literal["TackyBitwiseAnd"] = "TackyBitwiseAnd"


class TackyBitwiseOr(TackyASTNode):
    node_type: Literal["TackyBitwiseOr"] = "TackyBitwiseOr"


class TackyBitwiseXor(TackyASTNode):
    node_type: Literal["TackyBitwiseXor"] = "TackyBitwiseXor"


class TackyLeftShift(TackyASTNode):
    node_type: Literal["TackyLeftShift"] = "TackyLeftShift"


class TackyRightShift(TackyASTNode):
    node_type: Literal["TackyRightShift"] = "TackyRightShift"


TackyBinaryOperator = Union[
    TackyAdd,
    TackySubtract,
    TackyMultiply,
    TackyDivide,
    TackyModulo,
    TackyBitwiseAnd,
    TackyBitwiseOr,
    TackyBitwiseXor,
    TackyLeftShift,
    TackyRightShift,
]


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

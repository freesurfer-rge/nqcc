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


class TackyEqualTo(TackyASTNode):
    node_type: Literal["TackyEqualTo"] = "TackyEqualTo"


class TackyNotEqualTo(TackyASTNode):
    node_type: Literal["TackyNotEqualTo"] = "TackyNotEqualTo"


class TackyLessThan(TackyASTNode):
    node_type: Literal["TackyLessThan"] = "TackyLessThan"


class TackyLessThanOrEqual(TackyASTNode):
    node_type: Literal["TackyLessThanOrEqual"] = "TackyLessThanOrEqual"


class TackyGreaterThan(TackyASTNode):
    node_type: Literal["TackyGreaterThan"] = "TackyGreaterThan"


class TackyGreaterThanOrEqual(TackyASTNode):
    node_type: Literal["TackyGreaterThanOrEqual"] = "TackyGreaterThanOrEqual"


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
    TackyEqualTo,
    TackyNotEqualTo,
    TackyLessThan,
    TackyLessThanOrEqual,
    TackyGreaterThan,
    TackyGreaterThanOrEqual,
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


class TackyCopyNode(TackyASTNode):
    node_type: Literal["TackyCopyNode"] = "TackyCopyNode"
    src: TackyValue
    dst: TackyValue


class TackyJumpNode(TackyASTNode):
    node_type: Literal["TackyJumpNode"] = "TackyJumpNode"
    target: str


class TackyJumpIfZeroNode(TackyASTNode):
    node_type: Literal["TackyJumpIfZeroNode"] = "TackyJumpIfZeroNode"
    target: str
    condition: TackyValue


class TackyJumpIfNotZeroNode(TackyASTNode):
    node_type: Literal["TackyJumpIfNotZeroNode"] = "TackyJumpIfNotZeroNode"
    target: str
    condition: TackyValue


class TackyLabelNode(TackyASTNode):
    node_type: Literal["TackyLabelNode"] = "TackyLabelNode"
    identifier: str


TackyInstruction = Union[
    TackyReturnNode,
    TackyUnaryNode,
    TackyBinaryNode,
    TackyCopyNode,
    TackyJumpNode,
    TackyJumpIfZeroNode,
    TackyJumpIfNotZeroNode,
    TackyLabelNode,
]


class TackyFunctionNode(TackyASTNode):
    node_type: Literal["TackyFunctionNode"] = "TackyFunctionNode"
    identifier: str
    instructions: list[TackyInstruction]


class TackyProgramNode(TackyASTNode):
    node_type: Literal["TackyProgramNode"] = "TackyProgramNode"
    function_definition: TackyFunctionNode

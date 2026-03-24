from typing import Literal, Union

from pydantic import BaseModel


class SourceASTNode(BaseModel):
    node_type: str
    start_position: int


class SourceConstantIntNode(SourceASTNode):
    node_type: Literal["SourceConstantIntNode"] = "SourceConstantIntNode"
    value: int


class SourceComplement(SourceASTNode):
    node_type: Literal["SourceComplementNode"] = "SourceComplementNode"


class SourceNegate(SourceASTNode):
    node_type: Literal["SourceNegateNode"] = "SourceNegateNode"

class SourceLogicalNot(SourceASTNode):
    node_type: Literal["SourceLogicalNot"] = "SourceLogicalNot"


SourceUnaryOperator = Union[SourceComplement, SourceNegate, SourceLogicalNot]


class SourceUnaryExpressionNode(SourceASTNode):
    node_type: Literal["SourceUnaryExpressionNode"] = "SourceUnaryExpressionNode"
    operator: SourceUnaryOperator
    expression: SourceExpressionNode


class SourceBinOp(SourceASTNode):
    precedence: int


class SourceBitwiseOr(SourceBinOp):
    node_type: Literal["SourceBitwiseOr"] = "SourceBitwiseOr"
    precedence: Literal[15] = 15


class SourceBitwiseXor(SourceBinOp):
    node_type: Literal["SourceBitwiseXor"] = "SourceBitwiseXor"
    precedence: Literal[20] = 20


class SourceBitwiseAnd(SourceBinOp):
    node_type: Literal["SourceBitwiseAnd"] = "SourceBitwiseAnd"
    precedence: Literal[25] = 25


class SourceLeftShift(SourceBinOp):
    node_type: Literal["SourceLeftShift"] = "SourceLeftShift"
    precedence: Literal[40] = 40


class SourceRightShift(SourceBinOp):
    node_type: Literal["SourceRightShift"] = "SourceRightShift"
    precedence: Literal[40] = 40


class SourceAdd(SourceBinOp):
    node_type: Literal["SourceAdd"] = "SourceAdd"
    precedence: Literal[45] = 45


class SourceSubtract(SourceBinOp):
    node_type: Literal["SourceSubtract"] = "SourceSubtract"
    precedence: Literal[45] = 45


class SourceMultiply(SourceBinOp):
    node_type: Literal["SourceMultiply"] = "SourceMultiply"
    precedence: Literal[50] = 50


class SourceDivide(SourceBinOp):
    node_type: Literal["SourceDivide"] = "SourceDivide"
    precedence: Literal[50] = 50


class SourceModulo(SourceBinOp):
    node_type: Literal["SourceModulo"] = "SourceModulo"
    precedence: Literal[50] = 50


SourceBinaryOperator = Union[
    SourceAdd,
    SourceSubtract,
    SourceMultiply,
    SourceDivide,
    SourceModulo,
    SourceBitwiseXor,
    SourceBitwiseAnd,
    SourceBitwiseOr,
    SourceLeftShift,
    SourceRightShift,
]


class SourceBinaryExpressionNode(SourceASTNode):
    node_type: Literal["SourceBinaryExpressionNode"] = "SourceBinaryExpressionNode"
    operator: SourceBinaryOperator
    left: SourceExpressionNode
    right: SourceExpressionNode


SourceExpressionNode = Union[
    SourceConstantIntNode, SourceUnaryExpressionNode, SourceBinaryExpressionNode
]


class SourceReturnNode(SourceASTNode):
    node_type: Literal["SourceReturnNode"] = "SourceReturnNode"
    value: SourceExpressionNode


SourceStatementNode = Union[SourceReturnNode]


class SourceFunctionNode(SourceASTNode):
    node_type: Literal["SourceFunctionNode"] = "SourceFunctionNode"
    identifier: str
    body: SourceStatementNode


class SourceProgramNode(SourceASTNode):
    node_type: Literal["SourceProgramNode"] = "SourceProgramNode"
    value: SourceFunctionNode

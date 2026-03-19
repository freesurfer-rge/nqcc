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


SourceUnaryOperator = Union[SourceComplement, SourceNegate]


class SourceUnaryExpressionNode(SourceASTNode):
    node_type: Literal["SourceUnaryExpressionNode"] = "SourceUnaryExpressionNode"
    operator: SourceUnaryOperator
    expression: SourceExpressionNode


class SourceBinOp(SourceASTNode):
    precedence: int


class SourceAddOperator(SourceBinOp):
    node_type: Literal["SourceAddOperator"] = "SourceAddOperator"
    precedence: Literal[45] = 45


class SourceSubtractOperator(SourceBinOp):
    node_type: Literal["SourceSubtractOperator"] = "SourceSubtractOperator"
    precedence: Literal[45] = 45


class SourceMultiplyOperator(SourceBinOp):
    node_type: Literal["SourceMultiplyOperator"] = "SourceMultiplyOperator"
    precedence: Literal[50] = 50


class SourceDivideOperator(SourceBinOp):
    node_type: Literal["SourceDivideOperator"] = "SourceDivideOperator"
    precedence: Literal[50] = 50


class SourceModuloOperator(SourceBinOp):
    node_type: Literal["SourceModuloOperator"] = "SourceModuloOperator"
    precedence: Literal[50] = 50


SourceBinaryOperator = Union[
    SourceAddOperator,
    SourceSubtractOperator,
    SourceMultiplyOperator,
    SourceDivideOperator,
    SourceModuloOperator,
]


class SourceBinaryExpressionNode(SourceASTNode):
    node_type: Literal["SourceBinaryExpressionNode"] = "SourceBinaryExpressionNode"
    operator: SourceBinaryOperator
    left: SourceExpressionNode
    right: SourceExpressionNode


SourceExpressionNode = Union[SourceConstantIntNode, SourceUnaryExpressionNode, SourceBinaryExpressionNode]


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

from typing import Literal, Union

from pydantic import BaseModel


class SourceASTNode(BaseModel):
    node_type: str
    start_position: int


class SourceConstantIntNode(SourceASTNode):
    node_type: Literal["SourceConstantIntNode"] = "SourceConstantIntNode"
    value: int


class SourceUnaryExpressionNode(SourceASTNode):
    expression: SourceExpressionNode


class SourceComplementNode(SourceUnaryExpressionNode):
    node_type: Literal["SourceComplementNode"] = "SourceComplementNode"


class SourceNegateNode(SourceUnaryExpressionNode):
    node_type: Literal["SourceNegateNode"] = "SourceNegateNode"


SourceUnaryNode = Union[SourceComplementNode, SourceNegateNode]


class SourceAddOperator(SourceASTNode):
    node_type: Literal["SourceAddOperator"] = "SourceAddOperator"


class SourceSubtractOperator(SourceASTNode):
    node_type: Literal["SourceSubtractOperator"] = "SourceSubtractOperator"


class SourceMultiplyOperator(SourceASTNode):
    node_type: Literal["SourceMultiplyOperator"] = "SourceMultiplyOperator"


class SourceDivideOperator(SourceASTNode):
    node_type: Literal["SourceDivideOperator"] = "SourceDivideOperator"


class SourceModuloOperator(SourceASTNode):
    node_type: Literal["SourceModuloOperator"] = "SourceModuloOperator"


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


SourceExpressionNode = Union[SourceConstantIntNode, SourceUnaryNode, SourceBinaryExpressionNode]


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

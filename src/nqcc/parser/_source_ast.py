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

SourceExpressionNode = Union[SourceConstantIntNode, SourceUnaryNode]


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

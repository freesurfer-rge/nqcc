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


class TackyComplementNode(TackyASTNode):
    node_type: Literal["TackyComplementNode"] = "TackyComplementNode"


class TackyNegateNode(TackyASTNode):
    node_type: Literal["TackyNegateNode"] = "TackyNegateNode"


TackyUnaryOperator = Union[TackyComplementNode, TackyNegateNode]

from typing import Literal, Union

from pydantic import BaseModel, Field


class AsmASTNode(BaseModel):
    node_type: str
    start_position: int


class AsmImmediateIntNode(AsmASTNode):
    node_type: Literal["AsmImmediateIntNode"] = "AsmImmediateIntNode"
    value: int


class AsmRegisterNode(AsmASTNode):
    node_type: Literal["AsmRegisterNode"] = "AsmRegisterNode"
    value: Literal["eax", "rbp", "rsp", "r10d"]


class AsmPseudoRegisterNode(AsmASTNode):
    node_type: Literal["AsmPseudoRegisterNode"] = "AsmPseudoRegisterNode"
    identifier: str


class AsmStackNode(AsmASTNode):
    node_type: Literal["AsmStackNode"] = "AsmStackNode"
    offset: int = Field(le=0)


AsmOperandNode = Union[AsmImmediateIntNode, AsmRegisterNode, AsmPseudoRegisterNode, AsmStackNode]


class AsmMovNode(AsmASTNode):
    node_type: Literal["AsmMovNode"] = "AsmMovNode"
    source: AsmOperandNode
    destination: AsmOperandNode


class AsmRetNode(AsmASTNode):
    node_type: Literal["AsmRetNode"] = "AsmRetNode"


class AsmNotOperator(AsmASTNode):
    node_type: Literal["AsmNotOperator"] = "AsmNotOperator"


class AsmNegOperator(AsmASTNode):
    node_type: Literal["AsmNegOperator"] = "AsmNegOperator"


AsmUnaryOperator = Union[AsmNotOperator, AsmNegOperator]


class AsmUnaryNode(AsmASTNode):
    node_type: Literal["AsmUnaryNode"] = "AsmUnaryNode"
    operator: AsmUnaryOperator
    source: AsmOperandNode


class AsmAllocateStackNode(AsmASTNode):
    node_type: Literal["AsmAllocateStackNode"] = "AsmAllocateStackNode"
    stack_size: int


AsmInstructionNode = Union[AsmMovNode, AsmRetNode, AsmUnaryNode, AsmAllocateStackNode]


class AsmFunctionNode(AsmASTNode):
    node_type: Literal["AsmFunctionNode"] = "AsmFunctionNode"
    identifier: str
    instructions: list[AsmInstructionNode]


class AsmProgramNode(AsmASTNode):
    node_type: Literal["AsmFunctionNode"] = "AsmFunctionNode"
    function_definition: AsmFunctionNode

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
    value: Literal["eax", "ecx", "cl", "edx", "rbp", "rsp", "r10d", "r11d"]


class AsmPseudoRegisterNode(AsmASTNode):
    node_type: Literal["AsmPseudoRegisterNode"] = "AsmPseudoRegisterNode"
    identifier: str


class AsmStackNode(AsmASTNode):
    node_type: Literal["AsmStackNode"] = "AsmStackNode"
    offset: int = Field(le=0)


AsmOperandNode = Union[AsmImmediateIntNode, AsmRegisterNode, AsmPseudoRegisterNode, AsmStackNode]


class AsmMovNode(AsmASTNode):
    node_type: Literal["AsmMovNode"] = "AsmMovNode"
    src: AsmOperandNode
    dst: AsmOperandNode


class AsmRetNode(AsmASTNode):
    node_type: Literal["AsmRetNode"] = "AsmRetNode"


class AsmNot(AsmASTNode):
    node_type: Literal["AsmNot"] = "AsmNot"


class AsmNeg(AsmASTNode):
    node_type: Literal["AsmNeg"] = "AsmNeg"


AsmUnaryOperator = Union[AsmNot, AsmNeg]


class AsmUnaryNode(AsmASTNode):
    node_type: Literal["AsmUnaryNode"] = "AsmUnaryNode"
    operator: AsmUnaryOperator
    src: AsmOperandNode


class AsmAdd(AsmASTNode):
    node_type: Literal["AsmAdd"] = "AsmAdd"


class AsmSubtract(AsmASTNode):
    node_type: Literal["AsmSubtract"] = "AsmSubtract"


class AsmMultiply(AsmASTNode):
    node_type: Literal["AsmMultiply"] = "AsmMultiply"


class AsmBitwiseAnd(AsmASTNode):
    node_type: Literal["AsmBitwiseAnd"] = "AsmBitwiseAnd"


class AsmBitwiseOr(AsmASTNode):
    node_type: Literal["AsmBitwiseOr"] = "AsmBitwiseOr"


class AsmBitwiseXor(AsmASTNode):
    node_type: Literal["AsmBitwiseXor"] = "AsmBitwiseXor"


class AsmLeftShift(AsmASTNode):
    node_type: Literal["AsmLeftShift"] = "AsmLeftShift"


class AsmRightShift(AsmASTNode):
    node_type: Literal["AsmRightShift"] = "AsmRightShift"


AsmBinaryOperator = Union[
    AsmAdd,
    AsmSubtract,
    AsmMultiply,
    AsmBitwiseAnd,
    AsmBitwiseOr,
    AsmBitwiseXor,
    AsmLeftShift,
    AsmRightShift,
]


class AsmBinaryNode(AsmASTNode):
    # x86 operators are effecitve +=, -= and *=
    node_type: Literal["AsmBinaryNode"] = "AsmBinaryNode"
    operator: AsmBinaryOperator
    src: AsmOperandNode
    dst: AsmOperandNode


class AsmIDivNode(AsmASTNode):
    # x86 assembler requires separate handling of divide and modulo
    node_type: Literal["AsmIDivNode"] = "AsmIDivNode"
    src: AsmOperandNode


class AsmCdqNode(AsmASTNode):
    node_type: Literal["AsmCdqNode"] = "AsmCdqNode"


class AsmAllocateStackNode(AsmASTNode):
    node_type: Literal["AsmAllocateStackNode"] = "AsmAllocateStackNode"
    stack_size: int


AsmInstructionNode = Union[
    AsmMovNode,
    AsmRetNode,
    AsmUnaryNode,
    AsmAllocateStackNode,
    AsmBinaryNode,
    AsmIDivNode,
    AsmCdqNode,
]


class AsmFunctionNode(AsmASTNode):
    node_type: Literal["AsmFunctionNode"] = "AsmFunctionNode"
    identifier: str
    instructions: list[AsmInstructionNode]
    stack_size: int = Field(ge=0, default=0)


class AsmProgramNode(AsmASTNode):
    node_type: Literal["AsmFunctionNode"] = "AsmFunctionNode"
    function_definition: AsmFunctionNode

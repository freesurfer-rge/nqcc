from typing import Literal, Union

from pydantic import BaseModel

from nqcc.parser import (
    SourceConstantIntNode,
    SourceExpressionNode,
    SourceFunctionNode,
    SourceProgramNode,
    SourceReturnNode,
    SourceStatementNode,
)


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
    offset: int


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


def convert_expression_node(node: SourceExpressionNode) -> AsmOperandNode:
    match node:
        case SourceConstantIntNode():
            return AsmImmediateIntNode(start_position=node.start_position, value=node.value)

        case _:
            raise ValueError(f"Unrecognised: {node.model_dump_json()}")


def convert_statement_node(node: SourceStatementNode) -> list[AsmInstructionNode]:
    match node:
        case SourceReturnNode():
            mov_node = AsmMovNode(
                start_position=node.start_position,
                source=convert_expression_node(node.value),
                destination=AsmRegisterNode(start_position=node.value.start_position, value="eax"),
            )
            ret_node = AsmRetNode(start_position=mov_node.start_position)
            return [mov_node, ret_node]

        case _:
            raise ValueError(f"Unrecognised: {node.model_dump_json()}")


def convert_function_node(node: SourceFunctionNode) -> AsmFunctionNode:
    instructions = convert_statement_node(node.body)
    return AsmFunctionNode(
        start_position=node.start_position, identifier=node.identifier, instructions=instructions
    )


def convert_program_node(node: SourceProgramNode) -> AsmProgramNode:
    func_node = convert_function_node(node.value)
    return AsmProgramNode(start_position=node.start_position, value=func_node)

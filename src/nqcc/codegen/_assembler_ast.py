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

_INSTRUCTION_INDENT = "    "
_OPCODE_FIELD_WIDTH = 8
_SEP_WIDTH = 70
_SEP_CHAR = "="

class AsmASTNode(BaseModel):
    node_type: str
    start_position: int

    def emit_assembly_string(self) -> str:
        raise NotImplementedError()


class AsmImmediateIntNode(AsmASTNode):
    node_type: Literal["AsmImmediateIntNode"] = "AsmImmediateIntNode"
    value: int

    def emit_assembly_string(self) -> str:
        return f"${self.value}"


class AsmRegisterNode(AsmASTNode):
    node_type: Literal["AsmRegisterNode"] = "AsmRegisterNode"
    value: Literal["eax", "rbp", "rsp"]

    def emit_assembly_string(self) -> str:
        return f"%{self.value}"


AsmOperandNode = Union[AsmImmediateIntNode, AsmRegisterNode]


class AsmMovNode(AsmASTNode):
    node_type: Literal["AsmMovNode"] = "AsmMovNode"
    source: AsmOperandNode
    destination: AsmOperandNode

    def emit_assembly_string(self) -> str:
        opcode = "movl".ljust(_OPCODE_FIELD_WIDTH)
        src = self.source.emit_assembly_string()
        dst = self.destination.emit_assembly_string()
        return f"{opcode}{src}, {dst}"


class AsmRetNode(AsmASTNode):
    node_type: Literal["AsmRetNode"] = "AsmRetNode"

    def emit_assembly_string(self):
        return "ret"


AsmInstructionNode = Union[AsmMovNode, AsmRetNode]


class AsmFunctionNode(AsmASTNode):
    node_type: Literal["AsmFunctionNode"] = "AsmFunctionNode"
    identifier: str
    instructions: list[AsmInstructionNode]

    def emit_instructions(self) -> list[str]:
        result = []
        result.append(f"# Starting {self.identifier} ".ljust(_SEP_WIDTH, _SEP_CHAR))
        result.append(f"{_INSTRUCTION_INDENT}.globl {self.identifier}")
        result.append(f"{self.identifier}:")
        for instr in self.instructions:
            nxt = instr.emit_assembly_string()
            result.append(f"{_INSTRUCTION_INDENT}{nxt}")
        return result



class AsmProgramNode(AsmASTNode):
    node_type: Literal["AsmFunctionNode"] = "AsmFunctionNode"
    value: AsmFunctionNode

    def emit_instructions(self) -> list[str]:
        result = []
        result += self.value.emit_instructions()
        result.append('.section .note.GNU-stack, "",@progbits')
        return result


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

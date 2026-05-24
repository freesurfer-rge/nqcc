from typing import get_args

from ._assembler_ast import (
    AsmAllocateStackNode,
    AsmBinaryNode,
    AsmCallNode,
    AsmCdqNode,
    AsmCmpNode,
    AsmFunctionNode,
    AsmIDivNode,
    AsmImmediateIntNode,
    AsmInstructionNode,
    AsmJmpCCNode,
    AsmJmpNode,
    AsmLabelNode,
    AsmMovNode,
    AsmOperandNode,
    AsmProgramNode,
    AsmPseudoRegisterNode,
    AsmPushNode,
    AsmRegisterNode,
    AsmRetNode,
    AsmSetCCNode,
    AsmStackNode,
    AsmUnaryNode,
    AsmDeallocateStackNode,
)

FIRST_STACK_OFFSET = 0
STACK_DELTA = 4


class PseudoRegisterReplacer:
    def __init__(self) -> None:
        self._reset()

    def _reset(self) -> None:
        self.pseudo_map: dict[str, AsmStackNode] = {}
        self.curr_offset = FIRST_STACK_OFFSET

    def get_updated_operand(self, operand: AsmOperandNode) -> AsmOperandNode:
        match operand:
            case AsmImmediateIntNode():
                return operand
            case AsmRegisterNode():
                return operand
            case AsmPseudoRegisterNode():
                if operand.identifier in self.pseudo_map:
                    return self.pseudo_map[operand.identifier]
                self.curr_offset -= STACK_DELTA
                result = AsmStackNode(
                    start_position=operand.start_position, offset=self.curr_offset
                )
                self.pseudo_map[operand.identifier] = result
                return result
            case AsmStackNode():
                # Should we log a warning?
                return operand
            case _:
                raise ValueError(f"Unrecognised: {operand}")

    def update_instruction(self, asm_instr: AsmInstructionNode):
        match asm_instr:
            case AsmMovNode():
                asm_instr.src = self.get_updated_operand(asm_instr.src)
                asm_instr.dst = self.get_updated_operand(asm_instr.dst)
            case AsmUnaryNode():
                asm_instr.src = self.get_updated_operand(asm_instr.src)
            case AsmBinaryNode():
                asm_instr.src = self.get_updated_operand(asm_instr.src)
                asm_instr.dst = self.get_updated_operand(asm_instr.dst)
            case AsmIDivNode():
                asm_instr.src = self.get_updated_operand(asm_instr.src)
            case AsmCmpNode():
                asm_instr.src = self.get_updated_operand(asm_instr.src)
                asm_instr.dst = self.get_updated_operand(asm_instr.dst)
            case AsmSetCCNode():
                asm_instr.src = self.get_updated_operand(asm_instr.src)
            case AsmPushNode():
                asm_instr.target = self.get_updated_operand(asm_instr.target)
            case (
                AsmRetNode()
                | AsmCdqNode()
                | AsmJmpCCNode()
                | AsmJmpNode()
                | AsmLabelNode()
                | AsmCallNode()
            ):
                return
            case AsmAllocateStackNode() | AsmDeallocateStackNode():
                # Another possible place to log a warning
                return
            case _:
                raise ValueError(f"Unrecognised {asm_instr}")

    def pseudo_replace_function(self, asm_func: AsmFunctionNode):
        assert isinstance(asm_func, AsmFunctionNode)
        self._reset()

        for instr in asm_func.instructions:
            if isinstance(instr, get_args(AsmInstructionNode)):
                self.update_instruction(instr)
            else:
                pass
        asm_func.stack_size = abs(self.curr_offset)

    def pseudo_replace(self, asm_program: AsmProgramNode):
        assert isinstance(asm_program, AsmProgramNode)

        for f in asm_program.function_definitions:
            self.pseudo_replace_function(f)

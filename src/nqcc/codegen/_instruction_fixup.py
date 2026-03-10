from ._assembler_ast import (
    AsmAllocateStackNode,
    AsmFunctionNode,
    AsmInstructionNode,
    AsmMovNode,
    AsmRegisterNode,
    AsmStackNode,
)


def apply_mov_fixup(instr: AsmMovNode) -> list[AsmInstructionNode]:
    if isinstance(instr.source, AsmStackNode) and isinstance(instr.destination, AsmStackNode):
        # Can't move from stack to stack; use r10d
        reg = AsmRegisterNode(start_position=instr.start_position, value="r10d")
        nxt0 = AsmMovNode(
            start_position=instr.start_position,
            source=instr.source,
            destination=reg,
        )
        nxt1 = AsmMovNode(
            start_position=instr.start_position, source=reg, destination=instr.destination
        )
        return [nxt0, nxt1]
    else:
        return [instr]


def fixup_function_instructions(asm_func: AsmFunctionNode):
    assert isinstance(asm_func, AsmFunctionNode)

    fixed_instructions: list[AsmInstructionNode] = []

    # First deal with stack allocation
    if asm_func.stack_size > 0:
        stack_instr = AsmAllocateStackNode(
            start_position=asm_func.start_position, stack_size=asm_func.stack_size
        )
        fixed_instructions.append(stack_instr)

    # Iterate and apply fix ups
    for instr in asm_func.instructions:
        match instr:
            case AsmMovNode():
                nxt_instrs = apply_mov_fixup(instr)
                fixed_instructions += nxt_instrs
            case _:
                fixed_instructions.append(instr)
    asm_func.instructions = fixed_instructions

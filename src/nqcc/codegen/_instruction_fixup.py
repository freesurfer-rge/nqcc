from ._assembler_ast import (
    AsmAdd,
    AsmAllocateStackNode,
    AsmBinaryNode,
    AsmBitwiseAnd,
    AsmBitwiseOr,
    AsmBitwiseXor,
    AsmFunctionNode,
    AsmIDivNode,
    AsmImmediateIntNode,
    AsmInstructionNode,
    AsmLeftShift,
    AsmMovNode,
    AsmMultiply,
    AsmProgramNode,
    AsmRegisterNode,
    AsmRightShift,
    AsmStackNode,
    AsmSubtract,
)


def apply_mov_fixup(instr: AsmMovNode) -> list[AsmInstructionNode]:
    if isinstance(instr.src, AsmStackNode) and isinstance(instr.dst, AsmStackNode):
        # Can't move from stack to stack; use r10d
        reg = AsmRegisterNode(start_position=instr.start_position, value="r10d")
        nxt0 = AsmMovNode(
            start_position=instr.start_position,
            src=instr.src,
            dst=reg,
        )
        nxt1 = AsmMovNode(start_position=instr.start_position, src=reg, dst=instr.dst)
        return [nxt0, nxt1]
    else:
        return [instr]


def apply_idiv_fixup(instr: AsmIDivNode) -> list[AsmInstructionNode]:
    if isinstance(instr.src, AsmImmediateIntNode):
        # Instruction must act on register
        reg = AsmRegisterNode(start_position=instr.start_position, value="r10d")
        nxt0 = AsmMovNode(start_position=instr.start_position, src=instr.src, dst=reg)
        nxt1 = AsmIDivNode(start_position=instr.start_position, src=reg)
        return [nxt0, nxt1]
    else:
        return [instr]


def apply_binary_fixup(instr: AsmBinaryNode) -> list[AsmInstructionNode]:
    match instr.operator:
        case AsmAdd() | AsmSubtract() | AsmBitwiseAnd() | AsmBitwiseOr() | AsmBitwiseXor():
            if isinstance(instr.src, AsmStackNode):
                # src cannot be on the stack
                reg = AsmRegisterNode(start_position=instr.start_position, value="r10d")
                nxt0 = AsmMovNode(start_position=instr.start_position, src=instr.src, dst=reg)
                nxt1 = AsmBinaryNode(
                    start_position=instr.start_position,
                    operator=instr.operator,
                    src=nxt0.dst,
                    dst=instr.dst,
                )
                return [nxt0, nxt1]
            else:
                return [instr]
        case AsmLeftShift() | AsmRightShift():
            if not isinstance(instr.src, AsmImmediateIntNode):
                # Have to use CL/ECX for number of places to shift
                # Note that CL is the least significant byte of ECX
                reg = AsmRegisterNode(start_position=instr.start_position, value="ecx")
                sub_reg = AsmRegisterNode(start_position=instr.start_position, value="cl")
                nxt0 = AsmMovNode(start_position=instr.start_position, src=instr.src, dst=reg)
                nxt1 = AsmBinaryNode(
                    start_position=instr.start_position,
                    operator=instr.operator,
                    src=sub_reg,
                    dst=instr.dst,
                )
                return [nxt0, nxt1]
            else:
                return [instr]
        case AsmMultiply():
            if isinstance(instr.dst, AsmStackNode):
                # This is a dst fixup (dst cannot be on stack), so use r11d
                reg = AsmRegisterNode(start_position=instr.start_position, value="r11d")
                nxt0 = AsmMovNode(start_position=instr.start_position, src=instr.dst, dst=reg)
                nxt1 = AsmBinaryNode(
                    start_position=instr.start_position,
                    operator=instr.operator,
                    src=instr.src,
                    dst=reg,
                )
                nxt2 = AsmMovNode(start_position=instr.start_position, src=reg, dst=instr.dst)
                return [nxt0, nxt1, nxt2]
            else:
                return [instr]
        case _:
            raise ValueError(f"Unrecognised: {instr}")


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
            case AsmIDivNode():
                nxt_instrs = apply_idiv_fixup(instr)
                fixed_instructions += nxt_instrs
            case AsmBinaryNode():
                nxt_instrs = apply_binary_fixup(instr)
                fixed_instructions += nxt_instrs
            case _:
                fixed_instructions.append(instr)
    asm_func.instructions = fixed_instructions


def fixup_program_instructions(asm_prog: AsmProgramNode):
    assert isinstance(asm_prog, AsmProgramNode)

    fixup_function_instructions(asm_prog.function_definition)

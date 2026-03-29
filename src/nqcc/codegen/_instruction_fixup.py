from ._assembler_ast import (
    AsmAdd,
    AsmAllocateStackNode,
    AsmBinaryNode,
    AsmBitwiseAnd,
    AsmBitwiseOr,
    AsmBitwiseXor,
    AsmCmpNode,
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
        # Can't move from stack to stack; use R10
        reg = AsmRegisterNode(start_position=instr.start_position, value="R10")
        nxt0 = AsmMovNode(
            start_position=instr.start_position,
            src=instr.src,
            dst=reg,
        )
        nxt1 = AsmMovNode(start_position=instr.start_position, src=reg, dst=instr.dst)
        return [nxt0, nxt1]
    else:
        return [instr]


def apply_cmp_fixup(instr: AsmCmpNode) -> list[AsmInstructionNode]:
    if isinstance(instr.src, AsmStackNode) and isinstance(instr.dst, AsmStackNode):
        # Can't have two stack operands; use R10
        reg = AsmRegisterNode(start_position=instr.start_position, value="R10")
        nxt0 = AsmMovNode(
            start_position=instr.start_position,
            src=instr.src,
            dst=reg,
        )
        nxt1 = AsmCmpNode(start_position=instr.start_position, src=reg, dst=instr.dst)
        return [nxt0, nxt1]
    elif isinstance(instr.dst, AsmImmediateIntNode):
        # 'dst' operand can't be a constant (this is effectively a subtract)
        reg = AsmRegisterNode(start_position=instr.start_position, value="R11")
        i_0 = AsmMovNode(start_position=instr.start_position, src=instr.dst, dst=reg)
        i_1 = AsmCmpNode(start_position=instr.start_position, src=instr.src, dst=reg)
        return [i_0, i_1]
    else:
        return [instr]


def apply_idiv_fixup(instr: AsmIDivNode) -> list[AsmInstructionNode]:
    if isinstance(instr.src, AsmImmediateIntNode):
        # Instruction must act on register
        reg = AsmRegisterNode(start_position=instr.start_position, value="R10")
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
                reg = AsmRegisterNode(start_position=instr.start_position, value="R10")
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
                reg = AsmRegisterNode(start_position=instr.start_position, value="CX")
                nxt0 = AsmMovNode(start_position=instr.start_position, src=instr.src, dst=reg)
                nxt1 = AsmBinaryNode(
                    start_position=instr.start_position,
                    operator=instr.operator,
                    src=reg,
                    dst=instr.dst,
                )
                return [nxt0, nxt1]
            else:
                return [instr]
        case AsmMultiply():
            if isinstance(instr.dst, AsmStackNode):
                # This is a dst fixup (dst cannot be on stack), so use R11
                reg = AsmRegisterNode(start_position=instr.start_position, value="R11")
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

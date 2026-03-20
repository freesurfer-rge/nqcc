import pathlib

from nqcc.codegen import (
    AsmAdd,
    AsmAllocateStackNode,
    AsmBinaryNode,
    AsmBinaryOperator,
    AsmCdqNode,
    AsmFunctionNode,
    AsmIDivNode,
    AsmImmediateIntNode,
    AsmInstructionNode,
    AsmMovNode,
    AsmMultiply,
    AsmNeg,
    AsmNot,
    AsmOperandNode,
    AsmProgramNode,
    AsmRegisterNode,
    AsmRetNode,
    AsmStackNode,
    AsmSubtract,
    AsmUnaryNode,
    AsmUnaryOperator,
)

ASSEMBLY_EXTENSION = ".s"


_INSTRUCTION_INDENT = "    "
_OPCODE_FIELD_WIDTH = 8
_SEP_WIDTH = 70
_SEP_CHAR = "="


def get_operand_assembler(operand_node: AsmOperandNode) -> str:
    match operand_node:
        case v if isinstance(v, AsmImmediateIntNode):
            return f"${operand_node.value}"
        case v if isinstance(v, AsmRegisterNode):
            return f"%{operand_node.value}"
        case v if isinstance(v, AsmStackNode):
            return f"{operand_node.offset}(%rbp)"
        case _:
            raise ValueError(f"Unrecognised: {operand_node}")


def get_unary_opcode(unary_operator: AsmUnaryOperator) -> str:
    match unary_operator:
        case AsmNeg():
            return "negl"
        case AsmNot():
            return "notl"
        case _:
            raise ValueError(f"Unrecognised: {unary_operator}")


def get_binary_opcode(binary_operator: AsmBinaryOperator) -> str:
    match binary_operator:
        case AsmAdd():
            return "addl"
        case AsmSubtract():
            return "subl"
        case AsmMultiply():
            return "imull"
        case _:
            raise ValueError(f"Unrecognised: {binary_operator}")


def get_instruction_assembler(instr_node: AsmInstructionNode) -> str:
    match instr_node:
        case AsmAllocateStackNode():
            opcode = "subq".ljust(_OPCODE_FIELD_WIDTH)
            src = f"${instr_node.stack_size}"
            dst = r"%rsp"
            return f"{opcode} {src}, {dst} # Allocate stack"
        case AsmMovNode():
            opcode = "movl".ljust(_OPCODE_FIELD_WIDTH)
            src = get_operand_assembler(instr_node.src)
            dst = get_operand_assembler(instr_node.dst)
            return f"{opcode} {src}, {dst}"
        case AsmRetNode():
            return "ret"
        case AsmBinaryNode():
            opcode = get_binary_opcode(instr_node.operator).ljust(_OPCODE_FIELD_WIDTH)
            src = get_operand_assembler(instr_node.src)
            dst = get_operand_assembler(instr_node.dst)
            return f"{opcode} {src}, {dst}"
        case AsmUnaryNode():
            opcode = get_unary_opcode(instr_node.operator).ljust(_OPCODE_FIELD_WIDTH)
            src = get_operand_assembler(instr_node.src)
            return f"{opcode} {src}"
        case AsmCdqNode():
            return "cdq"
        case AsmIDivNode():
            opcode = "idivl".ljust(_OPCODE_FIELD_WIDTH)
            src = get_operand_assembler(instr_node.src)
            return f"{opcode} {src}"
        case _:
            raise ValueError(f"Unrecognised: {instr_node}")


def stack_setup() -> list[str]:
    c0 = f"{_INSTRUCTION_INDENT}# Begin stack setup"
    op0 = "pushq".ljust(_OPCODE_FIELD_WIDTH)
    i0 = f"{_INSTRUCTION_INDENT}{op0} %rbp"
    op1 = "movq".ljust(_OPCODE_FIELD_WIDTH)
    i1 = f"{_INSTRUCTION_INDENT}{op1} %rsp, %rbp"
    c1 = f"{_INSTRUCTION_INDENT}# End stack setup"
    return [c0, i0, i1, c1]


def stack_teardown() -> list[str]:
    c0 = f"{_INSTRUCTION_INDENT}# Begin stack teardown"
    op0 = "movq".ljust(_OPCODE_FIELD_WIDTH)
    i0 = f"{_INSTRUCTION_INDENT}{op0} %rbp, %rsp"
    op1 = "popq".ljust(_OPCODE_FIELD_WIDTH)
    i1 = f"{_INSTRUCTION_INDENT}{op1} %rbp"
    c1 = f"{_INSTRUCTION_INDENT}# End stack teardown"
    return [c0, i0, i1, c1]


def get_function_assembler(func_node: AsmFunctionNode) -> list[str]:
    result = []
    result.append(f"# Starting {func_node.identifier} ".ljust(_SEP_WIDTH, _SEP_CHAR))
    result.append(f"{_INSTRUCTION_INDENT}.globl {func_node.identifier}")
    result.append(f"{func_node.identifier}:")

    result += stack_setup()

    for instr in func_node.instructions:
        nxt = get_instruction_assembler(instr)
        if nxt == "ret":
            # This could get troublesome if 'ret' isn't the last thing
            result += stack_teardown()
        result.append(f"{_INSTRUCTION_INDENT}{nxt}")
    return result


def get_program_assembler(prog_node: AsmProgramNode) -> list[str]:
    result = []
    result += get_function_assembler(prog_node.function_definition)
    result.append('.section .note.GNU-stack, "",@progbits')
    return result


def emit_assembler(
    asm_ast: AsmProgramNode, *, working_dir: pathlib.Path, file_stem: str
) -> pathlib.Path:
    assert working_dir.exists(), f"Unable to find working directory {working_dir}"

    asm_lines = get_program_assembler(asm_ast)

    output_file = file_stem + ASSEMBLY_EXTENSION
    output_path = working_dir / output_file
    with open(output_path, "w") as of:
        for al in asm_lines:
            of.write(al + "\n")

    return output_path

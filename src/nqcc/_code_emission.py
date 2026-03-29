import pathlib
from typing import Literal

from nqcc.codegen import (
    AsmAdd,
    AsmAllocateStackNode,
    AsmBinaryNode,
    AsmBinaryOperator,
    AsmBitwiseAnd,
    AsmBitwiseOr,
    AsmBitwiseXor,
    AsmCdqNode,
    AsmCmpNode,
    AsmSetCCNode,
    AsmFunctionNode,
    AsmIDivNode,
    AsmImmediateIntNode,
    AsmInstructionNode,
    AsmLeftShift,
    AsmMovNode,
    AsmMultiply,
    AsmNeg,
    AsmNot,
    AsmOperandNode,
    AsmProgramNode,
    AsmRegisterNode,
    AsmRegName,
    AsmRetNode,
    AsmRightShift,
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

SubRegister = Literal["L8", "4B"]

_REG_MAP: dict[AsmRegName, dict[SubRegister, str]] = {
    "AX": {"4B": "eax", "L8":"al"},
    "CX": {"4B": "ecx", "L8": "cl"},
    "DX": {"4B": "edx", "L8":"dl"},
    "R10": {"4B": "r10d", "L8":"r10b"},
    "R11": {"4B": "r11d", "L8":"r11b"},
}


def get_register(reg_name: AsmRegName, target: SubRegister) -> str:
    if reg_name not in _REG_MAP:
        raise ValueError(f"Unrecognised: {reg_name}")
    name_map = _REG_MAP[reg_name]
    if target not in name_map:
        raise ValueError(f"Unrecognised {reg_name} {target}")
    return name_map[target]


def get_operand_assembler(operand_node: AsmOperandNode, target: SubRegister) -> str:
    match operand_node:
        case AsmImmediateIntNode():
            return f"${operand_node.value}"
        case AsmRegisterNode():
            return f"%{get_register(operand_node.value, target)}"
        case AsmStackNode():
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
        case AsmBitwiseAnd():
            return "andl"
        case AsmBitwiseOr():
            return "orl"
        case AsmBitwiseXor():
            return "xorl"
        case AsmLeftShift():
            # Use arithmetic shift to preserve sign
            return "sall"
        case AsmRightShift():
            # Use arithmetic shift to preserve sign
            return "sarl"
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
            src = get_operand_assembler(instr_node.src, "4B")
            dst = get_operand_assembler(instr_node.dst, "4B")
            return f"{opcode} {src}, {dst}"
        case AsmRetNode():
            return "ret"
        case AsmBinaryNode():
            opcode = get_binary_opcode(instr_node.operator).ljust(_OPCODE_FIELD_WIDTH)
            src = get_operand_assembler(instr_node.src, "4B")
            dst = get_operand_assembler(instr_node.dst, "4B")
            return f"{opcode} {src}, {dst}"
        case AsmUnaryNode():
            opcode = get_unary_opcode(instr_node.operator).ljust(_OPCODE_FIELD_WIDTH)
            src = get_operand_assembler(instr_node.src, "4B")
            return f"{opcode} {src}"
        case AsmCdqNode():
            return "cdq"
        case AsmCmpNode():
            src = get_operand_assembler(instr_node.src, "4B")
            dst = get_operand_assembler(instr_node.dst, "4B")
            return f"cmpl {src}, {dst}"
        case AsmIDivNode():
            opcode = "idivl".ljust(_OPCODE_FIELD_WIDTH)
            src = get_operand_assembler(instr_node.src, "4B")
            return f"{opcode} {src}"
        case AsmSetCCNode():
            opcode = f"set{instr_node.cond_code.lower()}".ljust(_OPCODE_FIELD_WIDTH)
            src = get_operand_assembler(instr_node.src, "L8")
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

import pathlib

from nqcc.codegen import (
    AsmFunctionNode,
    AsmImmediateIntNode,
    AsmInstructionNode,
    AsmMovNode,
    AsmOperandNode,
    AsmProgramNode,
    AsmRegisterNode,
    AsmRetNode,
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
        case _:
            raise ValueError(f"Unrecognised: {operand_node}")


def get_instruction_assembler(instr_node: AsmInstructionNode) -> str:
    match instr_node:
        case v if isinstance(v, AsmMovNode):
            opcode = "movl".ljust(_OPCODE_FIELD_WIDTH)
            src = get_operand_assembler(instr_node.source)
            dst = get_operand_assembler(instr_node.destination)
            return f"{opcode}{src}, {dst}"
        case v if isinstance(v, AsmRetNode):
            return "ret"
        case _:
            raise ValueError(f"Unrecognised: {instr_node}")


def get_function_assembler(func_node: AsmFunctionNode) -> list[str]:
    result = []
    result.append(f"# Starting {func_node.identifier} ".ljust(_SEP_WIDTH, _SEP_CHAR))
    result.append(f"{_INSTRUCTION_INDENT}.globl {func_node.identifier}")
    result.append(f"{func_node.identifier}:")
    for instr in func_node.instructions:
        nxt = get_instruction_assembler(instr)
        result.append(f"{_INSTRUCTION_INDENT}{nxt}")
    return result


def get_program_assembler(prog_node: AsmProgramNode) -> list[str]:
    result = []
    result += get_function_assembler(prog_node.value)
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

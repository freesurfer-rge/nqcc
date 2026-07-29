# This enables namespace package support, allowing the nqcc package to be split
# across multiple distributions. See PEP 420 and the Python import system docs:
# https://docs.python.org/3/reference/import_system.html#namespace-packages
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._code_emission import emit_assembler
from ._invoke_gcc import generate_executable, generate_objectfile, preprocess_c_file

__all__ = ["emit_assembler", "generate_executable", "generate_objectfile", "preprocess_c_file"]

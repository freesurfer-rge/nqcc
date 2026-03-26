
import pytest

from .utils import SAMPLE_PROGRAM_DIR, compile_run_check


@pytest.mark.parametrize(
    "c_source_file",
    [
        "return_constant.c",
        "return_negative_constant.c",
        "return_bitwise_zero.c",
        "return_many_negatives.c",
    ],
)
def test_simple_return_values(
    c_source_file: str,
):
    target_file = SAMPLE_PROGRAM_DIR / c_source_file
    assert target_file.exists(), f"{target_file} not found"

    compile_run_check(target_file, macros=[])


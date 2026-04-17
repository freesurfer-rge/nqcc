
from nqcc.parser import SourceForNode, SourceWhileNode, SourceDoWhileNode

LABEL_MAP = {
    SourceForNode: "for",
    SourceWhileNode: "while",
    SourceDoWhileNode: "do"
}

class LoopLabeller:
    def __init__(self, *, function_name: str)->None:
        self._func_name = function_name
        self._nxt_loop = 0

    def get_loop_label(self, stmt:SourceForNode| SourceWhileNode| SourceDoWhileNode) -> str:
        label = f"{LABEL_MAP[type(stmt)]}_{self._func_name}_{self._nxt_loop}"
        self._nxt_loop += 1
        return label
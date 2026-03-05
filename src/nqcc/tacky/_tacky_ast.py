from typing import Literal, Union

from pydantic import BaseModel


class TackyASTNode(BaseModel):
    node_type: str
    start_position: int
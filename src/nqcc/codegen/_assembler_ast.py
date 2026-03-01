from pydantic import BaseModel


class AsmASTNode(BaseModel):
    node_type: str
    start_position: int

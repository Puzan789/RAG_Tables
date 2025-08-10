from pydantic import BaseModel
from typing_extensions import TypedDict


class GraphState(TypedDict):
    question: str
    generation: str
    documents: list


class UploadChunkSchema(BaseModel):
    summaries: list
    metadata: list

from datetime import datetime
from typing import Annotated

from fastapi.params import Query
from pydantic import BaseModel

"""Модели Pydantic"""

class DocumentPydantic(BaseModel):
    id: int
    path: str | None = None
    date: datetime | None = None

class DocumentRequest(BaseModel):
    id: Annotated[int, Query()]

class DocumentTextPydantic(BaseModel):
    id: int
    id_doc: int
    text: str

# back/schemas.py

from pydantic import BaseModel, ConfigDict # Import ConfigDict
from typing import Optional, List

# --- Todo Schemas ---

class TodoBase(BaseModel):
    text: str
    completed: Optional[bool] = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    text: Optional[str] = None
    completed: Optional[bool] = None

class Todo(TodoBase):
    id: int
    model_config = ConfigDict(from_attributes=True) # Use model_config instead of class Config

# --- AI Suggestion Schemas ---

class SuggestionRequest(BaseModel):
    tasks: List[str]

class SuggestionResponse(BaseModel):
    suggestions: List[str]

class SearchRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    id: int
    text: str
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
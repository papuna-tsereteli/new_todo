from pydantic import BaseModel
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
    class Config:
        from_attributes = True

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
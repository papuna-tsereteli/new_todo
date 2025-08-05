from contextlib import asynccontextmanager

from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from ai_suggester import get_suggestions_graph
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from reindex import reindex_all_todos

# <<< 1. Import the new vector DB client
from vector_db import vector_db_client

# Create all database tables
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("--- Application starting up... ---")
    # Use BackgroundTasks to run the check without blocking startup
    background_tasks = BackgroundTasks()
    background_tasks.add_task(reindex_all_todos)
    # The 'await' here is for the add_task, not the task itself.
    # The task will run in the background.
    await background_tasks()

    yield

    # Code to run on shutdown
    print("--- Application shutting down... ---")

app = FastAPI(lifespan=lifespan)

# Your origins list should be the one that works for you
origins = [
    "http://localhost",
    "http://localhost:8081",
    "http://127.0.0.1:8000",
    "http://192.168.100.225:8000",  # Example IP, keep yours
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Welcome to the To-Do App API"}


# --- AI Suggestions Endpoint (No Changes Needed) ---
@app.post("/todos/suggest", response_model=schemas.SuggestionResponse)
async def suggest_todos(request: schemas.SuggestionRequest):
    try:
        graph = get_suggestions_graph()
        result = await graph.ainvoke({"existing_tasks": request.tasks})
        return {"suggestions": result['suggestions']}
    except Exception as e:
        print(f"Error during AI suggestion: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate AI suggestions.")


# <<< 2. Add the new Vector Search Endpoint
@app.post("/todos/search", response_model=schemas.SearchResponse)
def search_for_todos(request: schemas.SearchRequest):
    """
    Searches for semantically similar to-do items using vector search.
    """
    try:
        # Define a minimum confidence score
        MIN_SCORE_THRESHOLD = 0.30  # <<< You can tune this value

        search_results = vector_db_client.search_todos(query=request.query)

        # <<< Filter the results based on the threshold
        filtered_results = [
            result for result in search_results if result.score >= MIN_SCORE_THRESHOLD
        ]

        # Format the (now filtered) results to match the Pydantic response model
        formatted_results = [
            schemas.SearchResult(
                id=result.id,
                text=result.payload.get('text', ''),
                score=result.score
            )
            for result in filtered_results
        ]
        return {"results": formatted_results}
    except Exception as e:
        print(f"Error during vector search: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform vector search.")


# --- Standard Todo Endpoints (with vector DB integration) ---

@app.post("/todos/", response_model=schemas.Todo)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    db_todo = models.Todo(text=todo.text)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    # <<< 3. Add the new to-do to our vector database
    try:
        vector_db_client.upsert_todo(todo_id=db_todo.id, todo_text=db_todo.text)
    except Exception as e:
        print(f"Error upserting vector for new todo {db_todo.id}: {e}")

    return db_todo


@app.get("/todos/", response_model=List[schemas.Todo])
def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    todos = db.query(models.Todo).offset(skip).limit(limit).all()
    return todos


@app.get("/todos/{todo_id}", response_model=schemas.Todo)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo


@app.put("/todos/{todo_id}", response_model=schemas.Todo)
def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    text_was_changed = todo.text is not None and todo.text != db_todo.text
    if todo.text is not None:
        db_todo.text = todo.text
    if todo.completed is not None:
        db_todo.completed = todo.completed

    db.commit()
    db.refresh(db_todo)

    # <<< 4. Update the vector only if the text was changed
    if text_was_changed:
        try:
            vector_db_client.upsert_todo(todo_id=db_todo.id, todo_text=db_todo.text)
        except Exception as e:
            print(f"Error upserting vector for updated todo {db_todo.id}: {e}")

    return db_todo


@app.delete("/todos/{todo_id}", response_model=schemas.Todo)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    # <<< 5. Before deleting from SQL, delete the vector
    try:
        vector_db_client.delete_todo_vector(todo_id=todo_id)
    except Exception as e:
        print(f"Error deleting vector for todo {todo_id}: {e}")

    db.delete(db_todo)
    db.commit()

    return db_todo
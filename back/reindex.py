# back/reindex.py

from sqlalchemy.orm import Session
from database import SessionLocal
import models
from vector_db import vector_db_client

def reindex_all_todos():
    """
    Reads all To-Do items from the SQL database and upserts their
    vectors into the Qdrant vector database.
    """
    print("--- AUTOMATED RE-INDEXING CHECK ---")
    db: Session = SessionLocal()
    try:
        # 1. Get all todos from the primary SQL database
        all_todos_in_sql = db.query(models.Todo).all()
        sql_count = len(all_todos_in_sql)

        # 2. Get vector count from Qdrant
        try:
            qdrant_count = vector_db_client.count_todos().count
        except Exception as e:
            # This can happen if the collection doesn't exist yet
            print(f"Could not get count from Qdrant (may be starting up): {e}")
            qdrant_count = 0

        print(f"SQL DB Count: {sql_count}, Qdrant Vector Count: {qdrant_count}")

        # 3. The Core Logic: Re-index if SQL has data and Qdrant is empty
        if sql_count > 0 and qdrant_count == 0:
            print("Detected mismatch. Starting re-indexing in the background...")
            for todo in all_todos_in_sql:
                try:
                    vector_db_client.upsert_todo(todo_id=todo.id, todo_text=todo.text)
                except Exception as e:
                    print(f"Error indexing todo ID {todo.id}: {e}")
            print("--- Background re-indexing complete! ---")
        else:
            print("Databases are in sync. No re-indexing needed.")

    finally:
        db.close()

if __name__ == "__main__":
    reindex_all_todos()
import numpy as np
import os # Add this import

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv # Add this import
load_dotenv() # Add this line

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333)) # Use int to cast the port
COLLECTION_NAME = "todos"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class VectorDB:
    def __init__(self):
        """
        Initializes the Qdrant client, the embedding model, and ensures the
        collection exists in Qdrant.
        """
        # Initialize the Qdrant client
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

        # Load the sentence transformer model from HuggingFace
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)

        # Get the dimension size of the model's embeddings
        embedding_size = self.embedding_model.get_sentence_embedding_dimension()

        # Check if the collection already exists
        try:
            self.client.get_collection(collection_name=COLLECTION_NAME)
            print(f"Collection '{COLLECTION_NAME}' already exists.")
        except Exception:
            print(f"Collection '{COLLECTION_NAME}' not found. Creating new collection.")
            # If it doesn't exist, create it
            self.client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=models.Distance.COSINE  # Cosine similarity is good for text
                ),
            )
            print(f"Collection '{COLLECTION_NAME}' created successfully.")

    def _get_embedding(self, text: str) -> np.ndarray:
        """Helper function to create an embedding for a given text."""
        return self.embedding_model.encode(text, convert_to_tensor=False)

    def upsert_todo(self, todo_id: int, todo_text: str):
        """
        Creates an embedding for a to-do item and upserts (updates or inserts)
        it into the Qdrant collection.
        """
        vector = self._get_embedding(todo_text)

        # Upsert the point into the collection
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=todo_id,
                    vector=vector.tolist(),
                    # We can store the original text as a payload for easy retrieval
                    payload={"text": todo_text}
                )
            ],
            wait=True  # Wait for the operation to complete
        )
        print(f"Upserted vector for To-Do ID: {todo_id}")

    def search_todos(self, query: str, limit: int = 5) -> list:
        """
        Searches for to-do items that are semantically similar to the query.
        """
        query_vector = self._get_embedding(query)

        search_result = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector.tolist(),
            limit=limit,
            with_payload=True  # Include the payload in the search results
        )
        # The result is a list of ScoredPoint objects
        return search_result

    def delete_todo_vector(self, todo_id: int):
        """
        Deletes a vector from the Qdrant collection by its ID.
        """
        self.client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=models.PointIdsList(points=[todo_id]),
            wait=True
        )
        print(f"Deleted vector for To-Do ID: {todo_id}")


# Create a single instance to be used across the application
vector_db_client = VectorDB()
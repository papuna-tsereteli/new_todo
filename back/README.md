# To-Do App Backend

This repository contains the backend server for the To-Do App, built with Python, FastAPI, and PostgreSQL. It provides a RESTful API for creating, reading, updating, and deleting tasks.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

* **Python 3.7+**: [Download from python.org](https://www.python.org/downloads/)
* **PostgreSQL**: [Download from postgresql.org](https://www.postgresql.org/download/)

## Setup Instructions

Follow these steps to get the backend server running locally.

### 1. Clone the Repository

```bash
git clone <url>
cd back
```

### 2. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies.

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

Install all the required Python packages.

```bash
pip install -r requirements.txt
```

### 4. Set Up the PostgreSQL Database

1.  Open `psql` or your preferred PostgreSQL client.
2.  Create a new database for the application.

    ```sql
    CREATE DATABASE todo_db;
    ```

### 5. Configure Environment Variables

1.  Create a file named `.env` in the root of the project directory.
2.  Add your database connection URL to this file. **Remember to replace `YOUR_PASSWORD` and use the correct port if you changed it from the default.**
3. Your Gemini api key. (Current one is working for now)**

    ```env
    DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:port/todo_db"
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"

    ```

## Running the Application

Once the setup is complete, you can run the server using `uvicorn`.

```bash
from todo/
uvicorn back.main:app --host 0.0.0.0 --port 8000

```



The API will be available at `http://your_ip:8000`.

## API Documentation

FastAPI provides automatic interactive API documentation. Once the server is running, you can access it at:

* **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## API Endpoints

| Method | Endpoint         | Description                   |
| :----- | :--------------- | :---------------------------- |
| `GET`  | `/todos/`        | Retrieve all tasks.           |
| `POST` | `/todos/`        | Create a new task.            |
| `GET`  | `/todos/{id}`    | Retrieve a single task by ID. |
| `PUT`  | `/todos/{id}`    | Update a task by ID.          |
| `DELETE`| `/todos/{id}`    | Delete a task by ID.          |


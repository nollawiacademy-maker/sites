
from contextlib import asynccontextmanager
from pathlib import Path
import re
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DB_PATH = BASE_DIR / "portfolio.db"

STATIC_DIR.mkdir(exist_ok=True)


def get_connection():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Personal Portfolio API",
    description="Backend for my personal portfolio website",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ContactMessage(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    message: str = Field(min_length=5, max_length=5000)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.fullmatch(pattern, value):
            raise ValueError("Please enter a valid email address.")
        return value


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Portfolio backend is running."}


@app.post("/api/contact", status_code=201)
def create_message(contact: ContactMessage):
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO messages (name, email, message)
                VALUES (?, ?, ?)
                """,
                (contact.name, contact.email, contact.message),
            )
            message_id = cursor.lastrowid

        return {
            "success": True,
            "message": "Thank you! Your message was saved successfully.",
            "id": message_id,
        }

    except sqlite3.Error:
        raise HTTPException(
            status_code=500,
            detail="The message could not be saved. Please try again later.",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
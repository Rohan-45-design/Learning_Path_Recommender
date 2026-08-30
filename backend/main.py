from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.routes import courses
from rag.api.routes import router as rag_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event to initialize tables on startup."""
    init_db()
    yield


app = FastAPI(
    title="Learning Path Recommender API",
    description="Backend API and database service for managing courses and RAG recommendations.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware (configured for Next.js frontend on localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount courses router
app.include_router(courses.router)

# Mount RAG router
app.include_router(rag_router)


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint to verify backend service status."""
    return {"status": "ok", "service": "Learning Path Recommender Backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

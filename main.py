import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag.api.routes import router as rag_router

app = FastAPI(
    title="PathAI Learning Path RAG System",
    description="Domain-specific grounded RAG API for learning paths, resource retrieval, and AI mentorship.",
    version="1.0.0"
)

# Enable CORS for frontend / UI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rag_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to PathAI RAG System",
        "docs": "/docs",
        "chat_endpoint": "/rag/chat",
        "retrieve_endpoint": "/rag/retrieve"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

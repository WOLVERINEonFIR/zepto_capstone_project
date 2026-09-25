from fastapi import FastAPI

from graph import graph
from models import AskRequest, SupportResponse


app = FastAPI(
    title="Zepto Support Assistant",
    description="Deterministic RAG-based Zepto policy support assistant.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Zepto Support Assistant is running."
    }


@app.post("/ask", response_model=SupportResponse)
def ask(request: AskRequest):
    result = graph.invoke({
        "query": request.query
    })

    return SupportResponse(
        answer=result["answer"],
        sources=result["sources"],
        confidence=result["confidence"],
    )
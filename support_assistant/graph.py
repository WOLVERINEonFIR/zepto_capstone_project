import os
from typing import TypedDict

import chromadb
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, START, END

from models import SupportResponse


POLICY_KEYWORDS = [
    "delivery",
    "return",
    "refund",
    "membership",
    "tracking",
    "cancel",
    "gift card",
    "support hours",
]


class SupportState(TypedDict, total=False):
    query: str
    intent: str
    retrieved_documents: list[str]
    retrieved_ids: list[str]
    answer: str
    sources: list[str]
    confidence: float


# Load the local embedding model and Chroma collection.
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("zepto_policies")


def classify_intent(state: SupportState):
    query = state["query"].lower()

    if any(keyword in query for keyword in POLICY_KEYWORDS):
        intent = "policy_question"
    else:
        intent = "general_question"

    return {"intent": intent}


def retrieve_and_answer(state: SupportState):
    query = state["query"]

    query_embedding = MODEL.encode(
        [query],
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3,
    )

    documents = results["documents"][0]
    ids = results["ids"][0]

    top_chunk_snippet = documents[0][:200]

    answer = (
        f"Based on the retrieved context: {top_chunk_snippet}"
    )

    response = SupportResponse(
        answer=answer,
        sources=ids,
        confidence=1.0,
    )

    return {
        "retrieved_documents": documents,
        "retrieved_ids": ids,
        "answer": response.answer,
        "sources": response.sources,
        "confidence": response.confidence,
    }


def is_mock_mode():
    return os.getenv("MOCK_LLM", "1") == "1"


def validate_llm_output(raw_output):
    try:
        if isinstance(raw_output, str):
            import json
            raw_output = json.loads(raw_output)

        return SupportResponse.model_validate(raw_output)

    except Exception:
        return None


def generate_with_retry(generate_function, max_retries=2):
    last_output = None

    for attempt in range(max_retries + 1):
        if attempt == 0:
            instruction = None
        else:
            instruction = (
                "Your previous response was invalid. "
                "Return ONLY valid JSON with exactly these fields: "
                "answer (string), sources (list of strings), "
                "confidence (number between 0 and 1)."
            )

        last_output = generate_function(instruction)

        validated = validate_llm_output(last_output)

        if validated is not None:
            return validated

    raise ValueError(
        "LLM output remained invalid after 2 corrective retries."
    )

def direct_answer(state: SupportState):
    response = SupportResponse(
        answer="I can only answer questions about Zepto policies right now.",
        sources=[],
        confidence=1.0,
    )

    return {
        "answer": response.answer,
        "sources": response.sources,
        "confidence": response.confidence,
    }


def route_intent(state: SupportState):
    return state["intent"]


builder = StateGraph(SupportState)

builder.add_node("classify_intent", classify_intent)
builder.add_node("retrieve_and_answer", retrieve_and_answer)
builder.add_node("direct_answer", direct_answer)

builder.add_edge(START, "classify_intent")

builder.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "policy_question": "retrieve_and_answer",
        "general_question": "direct_answer",
    },
)

builder.add_edge("retrieve_and_answer", END)
builder.add_edge("direct_answer", END)

graph = builder.compile()
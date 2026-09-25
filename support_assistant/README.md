# Zepto Support Assistant

A deterministic, retrieval-augmented customer-support assistant for Zepto policy questions.

The graded default uses a local embedding model, ChromaDB retrieval, and deterministic mock responses. No external LLM API is required.

## Architecture

```text
                 ┌──────────────────┐
                 │   8 Policy Docs  │
                 │     docs/*.txt   │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │    ingest.py     │
                 │ Sentence         │
                 │ Transformer      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │     ChromaDB     │
                 │ zepto_policies   │
                 └────────┬─────────┘
                          │
                          │ top-3 retrieval
                          ▼
┌──────────────┐   ┌─────────────────────┐
│ POST /ask    │──▶│  classify_intent    │
│ FastAPI      │   └──────────┬──────────┘
└──────────────┘              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
          policy_question       general_question
                    │                   │
                    ▼                   ▼
          retrieve_and_answer     direct_answer
                    │                   │
                    └─────────┬─────────┘
                              ▼
                     Pydantic Response


Components
File	Purpose
docs/	Eight Zepto policy documents
ingest.py	Loads documents, creates embeddings, and stores them in ChromaDB
models.py	Pydantic request and response schemas
prompts.py	Structured prompt template for the optional real-LLM path
graph.py	LangGraph state, intent classification, retrieval, and answer generation
main.py	FastAPI application and /ask endpoint
Dockerfile	Container configuration
.dockerignore	Docker build exclusions
Ingestion and Embeddings

The corpus contains exactly eight policy documents.

Each document is currently treated as one chunk. The ingest.py script:

Loads doc_01.txt through doc_08.txt.
Generates embeddings using all-MiniLM-L6-v2.
Stores the embeddings and document text in ChromaDB.
Stores document_id and source filename as metadata.

The ChromaDB collection is:

zepto_policies

The local persistent database is stored in:

chroma_db/

Run ingestion from this directory:

python ingest.py

Successful ingestion reports:

Indexed documents: 8
Retrieval

Policy questions are embedded using the same all-MiniLM-L6-v2 model.

ChromaDB performs cosine-similarity retrieval and returns the top three matching documents.

For example:

Query:
How long does Zepto delivery take?

Retrieved:
doc_01
doc_08
doc_04

The most relevant document was doc_01, which contains the 10–30 minute delivery policy.

LangGraph

The graph contains three nodes:

classify_intent

Classifies the query using deterministic keyword matching in mock mode.

Policy keywords include:

delivery
return
refund
membership
tracking
cancel
gift card
support hours

The classifier produces either:

policy_question

or:

general_question
retrieve_and_answer

For policy questions:

Embed the query.
Retrieve the top three ChromaDB results.
Use the highest-ranked chunk.
Generate the deterministic mock response.
Return the retrieved document IDs as sources.

Mock answer format:

Based on the retrieved context: <top chunk snippet>
direct_answer

General questions receive the deterministic response:

I can only answer questions about Zepto policies right now.

No retrieval is performed for this route.

Graph flow
START
  |
  v
classify_intent
  |
  +---- policy_question ----> retrieve_and_answer ----> END
  |
  +---- general_question ---> direct_answer ---------> END
Output Schema

Responses are validated with Pydantic:

{
  "answer": "string",
  "sources": ["document_id"],
  "confidence": 1.0
}

confidence is constrained to the range 0.0 to 1.0.

In deterministic mock mode:

Retrieved document IDs are returned as sources.
General questions return an empty sources list.
confidence is always 1.0.
Prompt

prompts.py contains a structured prompt for the optional real-LLM path.

The template includes:

Role
Context
Task
Format
Length
Explicit negative constraint
Few-shot example

The negative constraint prevents the model from inventing Zepto policies, fees, time limits, or procedures that are absent from retrieved context.

Mock LLM Mode

The default mode is deterministic mock mode.

The environment variable is:

MOCK_LLM=1

The mock path does not require an external LLM API.

This is the default and graded execution path.

The code also contains validation and retry logic for the optional real-LLM path. Invalid structured LLM output can receive up to two additional corrective attempts before an error is raised.

FastAPI

Start the API from the support_assistant directory:

python -m uvicorn main:app --reload

The API is available at:

http://127.0.0.1:8000
Example 1: Policy question

Request:

{
  "query": "How long does Zepto delivery take?"
}

Response:

{
  "answer": "Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume. Standard del",
  "sources": [
    "doc_01",
    "doc_04",
    "doc_02"
  ],
  "confidence": 1.0
}
Example 2: General question

Request:

{
  "query": "What is the capital of France?"
}

Response:

{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}
Docker

A Dockerfile is included.

The image installs the required dependencies and runs ingest.py during the image build so that the ChromaDB index is created inside the image.

Build:

docker build -t zepto-support-assistant .

Run:

docker run -p 7860:7860 zepto-support-assistant

The container serves FastAPI on port 7860.

Docker execution was not tested in the development environment because Docker was not installed.

Run Order

From support_assistant/:

python ingest.py
python -m uvicorn main:app --reload

Then send POST requests to:

/ask

with:

{
  "query": "your question"
}

Save it.

### One correction before we move on

The README currently says:

> "The mock path does not require an external LLM API."

Correct.

But the `prompts.py` template is **not currently invoked by `graph.py`**. That's acceptable for the deterministic mock path, but the assignment describes the prompt as part of the optional real-LLM path. We have documented that distinction rather than pretending the prompt is used in mock mode.

Now run:

```powershell
Get-Item README.md

and make sure its size is greater than 0.
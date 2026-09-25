FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    langgraph \
    chromadb \
    sentence-transformers \
    pydantic

RUN python ingest.py

ENV MOCK_LLM=1

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
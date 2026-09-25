# Zepto Data & AI Platform

A three-module data and AI platform built as part of the Zepto Data & AI Platform capstone assignment.

The project contains:

1. **Module 1 — Data Pipeline & SQL Analytics**
2. **Module 2 — Advanced Analytics & Machine Learning**
3. **Module 3 — Support Assistant**

---

## Repository Structure

```text
Submission/
│
├── data_pipeline/
│   └── data_pipeline.ipynb
│
├── analytics/
│   ├── analytics.ipynb
│   ├── titanic.csv
│   └── best_titanic_classifier.joblib
│
├── support_assistant/
│   ├── docs/
│   │   ├── doc_01.txt
│   │   ├── doc_02.txt
│   │   ├── doc_03.txt
│   │   ├── doc_04.txt
│   │   ├── doc_05.txt
│   │   ├── doc_06.txt
│   │   ├── doc_07.txt
│   │   └── doc_08.txt
│   ├── ingest.py
│   ├── models.py
│   ├── prompts.py
│   ├── graph.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .dockerignore
│   └── README.md
│
├── .gitignore
└── README.md
1. Project Setup
Requirements
Python 3.10+
Git
Jupyter Notebook or JupyterLab
Internet connection for the initial data collection/model package installation where required
Docker is optional for Module 3

Create and activate a virtual environment:

python -m venv .venv
Windows
.venv\Scripts\activate
Linux/macOS
source .venv/bin/activate

Install the dependencies required by the modules.

For Module 3:

pip install -r support_assistant/requirements.txt

Module 1 and Module 2 are implemented as Jupyter notebooks and contain their required imports and processing steps.

2. Module 1 — Data Pipeline & SQL Analytics
Location
data_pipeline/data_pipeline.ipynb
Overview

Module 1 builds a data pipeline that:

Scrapes book data from the public Books to Scrape website.
Extracts and cleans the required fields.
Converts prices from GBP to INR.
Stores the data in a normalized SQLite database.
Performs SQL-based analytical queries.
Reproduces the SQL JOIN result using pandas.

The pipeline collected 517 books across 50 categories.

Running End-to-End

Open:

data_pipeline/data_pipeline.ipynb

Run all notebook cells sequentially.

The notebook performs the complete workflow from scraping through SQL analysis.

The scraping stage requires internet access.

The notebook creates the processed dataset and SQLite database during execution.

Design Decisions
Web scraping

requests and BeautifulSoup were used for straightforward HTTP retrieval and HTML parsing.

Data cleaning

Required fields were converted to appropriate numeric types. Invalid numeric values were handled using coercion, and rows that could not provide the required price/rating information were removed.

Currency conversion

Prices were converted using the specified fixed exchange rate:

price_inr = price_gbp × 105.50
Database design

The SQLite database uses two normalized tables:

categories
books

The books table references the category table through a foreign key.

This avoids repeatedly storing category information for every book.

SQL and pandas validation

SQL queries were used for the required analytical operations.

The SQL JOIN result was independently reproduced with a pandas merge and compared for equality.

3. Module 2 — Advanced Analytics & Machine Learning
Location
analytics/analytics.ipynb

Supporting files:

analytics/titanic.csv
analytics/best_titanic_classifier.joblib
Overview

Module 2 performs an end-to-end Titanic analytics and machine-learning workflow.

The notebook includes:

Data loading and inspection
Missing-value analysis
Data cleaning
Univariate analysis
Bivariate analysis
Correlation analysis
Multivariate analysis
Feature standardization sanity check
Classification
Class-imbalance analysis
Random Forest hyperparameter tuning
Regression
Model comparison
Model persistence
Running End-to-End

Open:

analytics/analytics.ipynb

Run the notebook cells sequentially.

The notebook initially loads the Titanic dataset and saves:

analytics/titanic.csv

The notebook then performs the complete analysis and modeling workflow.

The final fitted Random Forest pipeline is saved as:

analytics/best_titanic_classifier.joblib

The saved pipeline can subsequently be loaded with joblib for prediction.

Classification Models

Three classifiers are evaluated:

Logistic Regression
Decision Tree
Random Forest

The models use a preprocessing pipeline that separates numerical and categorical features.

Numerical features are imputed and standardized.

Categorical features are imputed and one-hot encoded.

The preprocessing is fitted only on the training data to prevent data leakage.

Class Imbalance

The Random Forest baseline is compared with:

Class-weight balancing
SMOTE

SMOTE is applied only to the training data.

Hyperparameter Tuning

Random Forest hyperparameters are tuned using GridSearchCV.

The search includes:

n_estimators
max_depth
max_features

The tuned Random Forest also uses out-of-bag evaluation.

Regression

A separate regression model predicts fare.

The regression workflow reports:

MAE
RMSE
R²
Adjusted R²

A residual plot is also used to inspect heteroscedasticity.

Design Decisions
Train/test split

Classification uses a stratified split so that the class proportions are preserved between training and test sets.

Preprocessing pipeline

ColumnTransformer and Pipeline are used so that preprocessing is fitted only on training data and applied consistently to test data.

Multiple classifiers

Logistic Regression, Decision Tree, and Random Forest provide different model structures for comparison rather than relying on a single algorithm.

Imbalance handling

Both class weighting and SMOTE were evaluated instead of assuming that class imbalance automatically requires oversampling.

Model selection

Models are compared using accuracy, precision, recall, F1-score, and ROC/AUC rather than relying on accuracy alone.

Model persistence

The complete fitted Random Forest pipeline is saved with joblib, allowing preprocessing and the model to be reloaded together.

4. Module 3 — Support Assistant
Location
support_assistant/
Overview

Module 3 implements a retrieval-augmented support assistant for Zepto policy questions.

The pipeline consists of:

Policy Documents
      ↓
Chunking
      ↓
Local Embeddings
      ↓
ChromaDB
      ↓
Query Embedding
      ↓
Top-3 Retrieval
      ↓
LangGraph Routing
      ↓
Validated Response
      ↓
FastAPI

The default mode is deterministic and does not require an external LLM API.

Setup

Move into the module directory:

cd support_assistant

Install dependencies:

pip install -r requirements.txt
Build the Vector Database

Run:

python ingest.py

This:

Loads the eight policy documents.
Chunks the documents.
Generates embeddings using:
all-MiniLM-L6-v2
Stores the embeddings in ChromaDB.

The generated ChromaDB directory is local runtime data and does not need to be committed.

Run the API

Start FastAPI:

uvicorn main:app --reload

The API runs locally at:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs
Test the API

Example policy question:

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"How long does Zepto delivery take?"}'

Example general question:

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"What is the capital of India?"}'

A policy question is routed through retrieval.

An unrelated question is routed to the direct-answer node.

Mock Mode

The default mode is:

MOCK_LLM=1

The mock mode does not make external LLM or network calls.

It provides deterministic:

Intent classification
Vector retrieval
Answer generation
Output validation

The optional LLM path can be selected with:

MOCK_LLM=0
LangGraph Workflow

The graph contains three main nodes:

classify_intent
        |
        +---- policy_question ----> retrieve_and_answer
        |
        +---- general_question ---> direct_answer

Policy questions use ChromaDB retrieval.

General questions receive the fixed mock response.

Output Schema

Responses follow:

{
  "answer": "string",
  "sources": ["document_id"],
  "confidence": 1.0
}

Pydantic validates the response structure and ensures that confidence remains between 0 and 1.

Docker

Build:

docker build -t zepto-support-assistant .

Run:

docker run -p 7860:7860 zepto-support-assistant

The Docker configuration runs the application on port 7860.

Design Decisions
Local embeddings

all-MiniLM-L6-v2 is used so that embedding generation does not require a paid external embedding API.

ChromaDB

ChromaDB provides local persistent vector storage and cosine-similarity retrieval.

LangGraph

LangGraph provides explicit workflow orchestration and conditional routing between policy retrieval and general-question handling.

Deterministic mock mode

The mock mode makes the graded baseline reproducible and avoids dependency on an external LLM service.

Pydantic

Pydantic provides a strict response contract for the API.

Source tracking

Retrieved document IDs are included in the response so that answers can be traced back to the policy corpus.

Regenerable vector database

The ChromaDB data is generated from the source documents rather than committed to Git. This keeps generated runtime data out of version control while preserving reproducibility.

5. End-to-End Module Summary
Module	Main Technology	Main Output
Module 1	Requests, BeautifulSoup, SQLite, SQL, pandas	Scraped and normalized book dataset with SQL analytics
Module 2	pandas, seaborn, scikit-learn, SMOTE, joblib	Analytics, classification/regression models, saved pipeline
Module 3	Sentence Transformers, ChromaDB, LangGraph, FastAPI	Retrieval-based Zepto support assistant
6. Git Workflow

The repository uses Git for version control.

The project was developed using a feature branch workflow.

The main branch contains the completed modules after feature integration.

The Module 3 work is developed separately on:

feature/module-3

and merged back into:

main

The feature branch contains multiple commits before merging.
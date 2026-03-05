# Phase 2: Embedding & Vector Store

This phase is responsible for taking the structured data from Phase 1 and converting it into searchable vector embeddings.

## Key Components
- **`ingest.py`**: The main script that reads `phase1/fund_data.json` and populates the vector database.
- **`chroma_db/`**: The persistent vector store containing indexed mutual fund details.

## How it works
1. **Load**: Reads the JSON output from Phase 1.
2. **Transform**: Formats the fund details (NAV, AUM, FAQs, About) into a unified text document for each fund.
3. **Embed**: Generates high-dimensional vector embeddings using the `all-MiniLM-L6-v2` model.
4. **Store**: Uses **ChromaDB** to store both the embeddings and the original metadata for retrieval in Phase 3.

## Usage
Run from the project root:
```bash
python3 phase2/ingest.py
```

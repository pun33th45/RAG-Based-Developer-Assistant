# DevInsight AI Architecture

DevInsight AI is organized as a small full-stack RAG system. The frontend handles upload and chat interactions, while the backend owns file parsing, chunking, vector indexing, retrieval, and response generation.

## RAG Flow

```text
User -> Upload -> Load Files -> Chunk -> Embed -> FAISS -> Query -> Retrieve -> LLM -> Answer
```

## Components

### Frontend

The React frontend provides two main workflows:

- Upload a codebase or document through `Upload.jsx`.
- Ask questions and inspect retrieved context through `Chat.jsx`.

The API client in `frontend/src/api.js` sends requests to the FastAPI backend using Axios.

### Backend API

FastAPI exposes:

- `POST /upload` for indexing uploaded files.
- `POST /query` for asking questions against the indexed content.
- `GET /health` for runtime health and configuration status.

### File Loading

Uploads are read from memory to avoid Windows and OneDrive file-lock issues. Zip archives are inspected safely before extracting individual file contents. Unsupported files and noisy directories such as `node_modules`, `.git`, and build outputs are skipped.

### Chunking

`RecursiveCharacterTextSplitter` splits code and text with separators that preserve common code boundaries such as classes, functions, exports, paragraphs, and lines.

### Embeddings

Gemini embeddings convert each chunk into a vector. The embedding wrapper intentionally embeds chunks one at a time so FAISS receives one vector per document, which prevents vector/document count mismatches.

### Vector Storage

FAISS stores vectors locally in `backend/storage/faiss`. This folder is ignored by Git because it is generated runtime state.

### Retrieval And Generation

For each query, the backend retrieves the top-k relevant chunks from FAISS, formats them as source-tagged context, and passes them into a LangChain prompt with the system instruction:

```text
You are a senior developer. Explain code clearly and identify bugs if present.
```

The response includes both the final answer and the retrieved source chunks so the UI can show grounded context.

# DevInsight AI API

Base URL for local development:

```text
http://localhost:8000
```

## Health Check

```http
GET /health
```

Returns runtime status and environment validation details.

Example response:

```json
{
  "status": "ok",
  "service": "DevInsight AI",
  "llm_configured": true,
  "runtime_issues": []
}
```

If the Gemini key is missing, `status` becomes `degraded` and `runtime_issues` explains the missing setting.

## Upload

```http
POST /upload
Content-Type: multipart/form-data
```

Form field:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `file` | File | Yes | Zip archive or supported source/document file |

Supported extensions include `.zip`, `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.txt`, `.md`, `.json`, `.yaml`, `.yml`, `.css`, and `.html`.

Example response:

```json
{
  "message": "Upload indexed successfully.",
  "filename": "repo.zip",
  "documents": 12,
  "chunks": 48
}
```

Common errors:

| Status | Reason |
| --- | --- |
| `400` | Unsupported file type, unsafe zip path, file too large, or no readable supported files |
| `500` | Embedding provider or vector store failure |

## Query

```http
POST /query
Content-Type: application/json
```

Request body:

```json
{
  "question": "Explain the architecture",
  "k": 5
}
```

Fields:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `question` | string | Yes | Developer question to answer from indexed context |
| `k` | integer | No | Number of chunks to retrieve, between 1 and 10 |

Example response:

```json
{
  "answer": "The project is organized around a FastAPI backend and a React frontend...",
  "sources": [
    {
      "source": "backend/app/main.py",
      "file_type": ".py",
      "content": "..."
    }
  ]
}
```

Common errors:

| Status | Reason |
| --- | --- |
| `400` | No documents indexed or invalid query payload |
| `500` | LLM provider failure |

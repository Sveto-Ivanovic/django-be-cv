# Vector Search App

The `vector_search` app is a core component of the Django backend, responsible for handling advanced search capabilities across vector databases. It provides API endpoints to perform semantic, lexical, and hybrid searches using both Supabase and Pinecone as vector stores.

## Overview

This application acts as the interface for querying embedded data. It relies heavily on utility functions defined in the `core` app (specifically within `apps.core.utilis`) to execute the actual search logic, abstracting the complexity of interacting with different vector databases and search algorithms.

## Endpoints

The app exposes two primary endpoints for vector searching, routed under the `/vectorsearch/` base path.

### 1. Supabase Vector Search

This endpoint handles search requests directed at the Supabase vector store.

**URL:** `/vectorsearch/retrieve_vectors_supabase/`
**Method:** `POST`
**Content-Type:** `application/json` or `application/x-www-form-urlencoded`

#### Request Parameters

| Parameter | Type | Required | Description | Constraints / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `query` | string | Yes | The search query string. | |
| `namespace` | string | Yes | The specific namespace or collection to search within. | |
| `table_name` | string | Yes | The name of the table storing the vectors. | Must match the model: `vector_search_3072` (gemini), `vector_search_2048` (jina), or `vector_search_1536` (embed-v4.0). |
| `model` | string | Yes | The embedding model used. | e.g., `gemini-embedding-001`, `jina-embeddings-v4`, `embed-v4.0`. |
| `mode` | string | No | The search mode. | Must be one of: `"semantic"`, `"lexical"`, or `"hybrid"`. Defaults to `"semantic"`. |
| `top_k` | integer | No | The number of top results to return. | Defaults to `5`. |
| `semantic_search_mode` | string | No | The distance metric for semantic search. | Defaults to `"cosine"`. Used for `semantic` and `hybrid` modes only. |
| `nearest_neighbor_settings` | object | No | Configuration for fetching surrounding context chunks. | See details below. |

**Nearest Neighbor Settings Object:**
- `get_all_neighbor_chunks` (boolean): Whether to fetch all chunks from the same page/document. Defaults to `False`.
- `nearest_chunks_n` (integer): Number of adjacent chunks to fetch. Defaults to `0`.
- `nearest_page_or_array_members_n` (integer): Number of adjacent pages/array members to fetch. Defaults to `0`.

#### Example Request

```json
POST /vectorsearch/retrieve_vectors_supabase/
Content-Type: application/json

{
  "query": "What are the key responsibilities of a backend developer?",
  "namespace": "user_123_resumes",
  "table_name": "vector_search_1536",
  "model": "embed-v4.0",
  "mode": "hybrid",
  "top_k": 3,
  "nearest_neighbor_settings": {
    "nearest_chunks_n": 2
  }
}
```

#### Example Response (Success)

**Semantic mode and Hybrid mode** — both include a `method` field reflecting `semantic_search_mode`:

```json
{
  "status": "success",
  "response": [
    {
      "id": "chunk_456",
      "content": "The backend developer is responsible for server-side logic...",
      "metadata": {"page": 1},
      "score": 0.92
    },
    {
      "id": "chunk_457",
      "content": "They also manage database integrations and API endpoints...",
      "metadata": {"page": 1},
      "score": 0.88
    }
  ],
  "method": "cosine"
}
```

**Lexical mode** — does **not** include a `method` field:

```json
{
  "status": "success",
  "response": [
    {
      "id": "chunk_456",
      "content": "The backend developer is responsible for server-side logic...",
      "metadata": {"page": 1},
      "score": 0.75
    }
  ]
}
```

#### Example Response (Error)

```json
{
  "status": "error",
  "response": "Invalid mode. Supported modes are 'semantic', 'lexical', and 'hybrid'."
}
```

```json
{
  "status": "error",
  "response": "Invalid table name or model provided."
}
```

### 2. Pinecone Vector Search

This endpoint handles search requests directed at the Pinecone vector store.

**URL:** `/vectorsearch/retrieve_vectors_pinecone/`
**Method:** `POST`
**Content-Type:** `application/json` or `application/x-www-form-urlencoded`

#### Request Parameters

| Parameter | Type | Required | Description | Constraints / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `query` | string | Yes | The search query string. | |
| `index_name` | string | Yes | The name of the Pinecone index for semantic search. | |
| `model` | string | Yes | The embedding model used. | |
| `mode` | string | No | The search mode. | Must be one of: `"semantic"`, `"lexical"`, or `"hybrid"`. Defaults to `"semantic"`. **Note:** unlike the Supabase endpoint, this value is not validated against the allowed list before use. |
| `index_name_lexical` | string | Conditional | The name of the Pinecone index for lexical search. | **Required** if `mode` is `"lexical"` or `"hybrid"`. |
| `top_k` | integer | No | The number of top results to return. | Defaults to `5`. |
| `nearest_neighbor_settings` | object | No | Configuration for fetching surrounding context chunks. | Same structure as Supabase endpoint. |

#### Example Request

```json
POST /vectorsearch/retrieve_vectors_pinecone/
Content-Type: application/json

{
  "query": "Machine learning experience",
  "index_name": "resume-embeddings-semantic",
  "index_name_lexical": "resume-embeddings-lexical",
  "model": "gemini-embedding-001",
  "mode": "hybrid",
  "top_k": 5
}
```

#### Example Response (Success)

All modes (`semantic`, `lexical`, `hybrid`) return the same response shape. **No `method` field is ever included**, unlike the Supabase endpoint:

```json
{
  "status": "success",
  "response": [
    {
      "id": "chunk_456",
      "content": "Machine learning experience with 5 years in NLP...",
      "metadata": {"page": 1},
      "score": 0.91
    },
    {
      "id": "chunk_457",
      "content": "Led development of a recommendation engine using ML...",
      "metadata": {"page": 2},
      "score": 0.87
    }
  ]
}
```

#### Example Response (Error)

`index_name_lexical` is required for **both** `lexical` and `hybrid` modes:

```json
{
  "status": "error",
  "response": "index_name_lexical is required for lexical search."
}
```

```json
{
  "status": "error",
  "response": "index_name_lexical is required for hybrid search."
}
```

## Authentication

Both endpoints require authentication. The system expects an `auth_id` to be attached to the request object (typically handled by middleware). If the `auth_id` is missing or invalid, the request will be rejected with a `400` or `500` status code. The system uses this ID to retrieve the user's specific API keys for Supabase or Pinecone.

Note: Pinecone endpoint expect that you inserted pinecone api key inside the usermanagement endpoints.

## Rate Limiting

Both endpoints are protected by rate limiting to prevent abuse. The current limit is set to **50 requests per day per IP address** (`rate="50/d"`). Exceeding this limit will result in the request being blocked.
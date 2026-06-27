# Chatbot API Documentation

## Overview

The Chatbot API provides an AI-powered conversational endpoint that supports:

* Multi-turn conversation memory
* Conversation persistence
* Context retrieval from Supabase and Pinecone vector stores
* Contact information extraction
* Prompt injection detection
* Message and conversation limits
* User-owned API keys (Gemini, Groq, Mistral)
* LLM fallback routing
* Conversation history storage

---

# Base URL

```http
http://localhost:8000/chatbot/
```

Production:

```http
https://api.yourdomain.com/chatbot/
```

---

# Authentication

This endpoint requires authentication.

Authentication middleware attaches:

```python
request.auth_id
```

which identifies the authenticated user.

If authentication fails:

```json
{
  "status": "error",
  "message": "Authentication ID is missing."
}
```

---

# Call Chatbot

Send a message to the chatbot and receive an AI-generated response.

## Endpoint

```http
POST /chatbot/call_chatbot/
```

---

## Request Body

### New Conversation

```json
{
  "question": "What is Retrieval Augmented Generation?",
  "llm_model": "gemini-2.5-flash"
}
```

### Existing Conversation

```json
{
  "question": "Can you give me an example?",
  "conv_id": "d8f69ca9-54ef-43db-8b64-fd67a2d3f95a",
  "llm_model": "gemini-2.5-flash"
}
```

### With Context Retrieval (Supabase)

```json
{
  "question": "Summarize the uploaded document.",,
  "llm_model": "gemini-2.5-flash"
  "supabase_metadata": {
    "namespace": "my-namespace",
    "table_name": "documents",
    "model": "text-embedding-3-small",
    "top_k": 5,
    "mode": "semantic",
    "semantic_search_mode": "cosine",
    "nearest_neighbor_settings": {
      "get_all_neighbor_chunks": false,
      "nearest_chunks_n": 2,
      "nearest_page_or_array_members_n": 1
    }
  }
}
```

### With Context Retrieval (Pinecone)

```json
{
  "question": "What does the policy say about refunds?",,
  "llm_model": "gemini-2.5-flash"
  "pinecone_metadata": {
    "index_name": "my-index",
    "index_name_lexical": "my-index-lexical",
    "model": "text-embedding-3-small",
    "top_k": 5,
    "mode": "hybrid",
    "nearest_neighbor_settings": {
      "get_all_neighbor_chunks": true,
      "nearest_chunks_n": 3,
      "nearest_page_or_array_members_n": 2
    }
  }
}
```

---

## Request Parameters

| Field              | Type   | Required | Description                                    |
| ------------------ | ------ | -------- | ---------------------------------------------- |
| question           | string | Yes      | User message                                   |
| conv_id            | string | No       | Existing conversation ID                       |
| supabase_metadata  | object | No       | Config for Supabase vector store retrieval     |
| pinecone_metadata  | object | No       | Config for Pinecone vector store retrieval     |

---

## supabase_metadata Fields

| Field                    | Type    | Required | Default    | Description                                           |
| ------------------------ | ------- | -------- | ---------- | ----------------------------------------------------- |
| namespace                | string  | Yes      | —          | Namespace to scope the search                         |
| table_name               | string  | Yes      | —          | Supabase table to query                               |
| model                    | string  | Yes      | —          | Embedding model name                                  |
| top_k                    | integer | No       | `5`        | Number of top results to retrieve                     |
| mode                     | string  | No       | `semantic` | Retrieval mode: `semantic`, `keyword`, or `hybrid`    |
| semantic_search_mode     | string  | No       | `cosine`   | Similarity metric: `cosine`, `l2`, or `ip`            |
| nearest_neighbor_settings| object  | No       | `{}`       | Settings for chunk expansion (see below)              |

---

## pinecone_metadata Fields

| Field                    | Type    | Required | Default    | Description                                           |
| ------------------------ | ------- | -------- | ---------- | ----------------------------------------------------- |
| index_name               | string  | Yes      | —          | Primary Pinecone index name                           |
| index_name_lexical       | string  | No       | `null`     | Lexical index name for hybrid search                  |
| model                    | string  | Yes      | —          | Embedding model name                                  |
| top_k                    | integer | No       | `5`        | Number of top results to retrieve                     |
| mode                     | string  | No       | `semantic` | Retrieval mode: `semantic`, `keyword`, or `hybrid`    |
| nearest_neighbor_settings| object  | No       | `{}`       | Settings for chunk expansion (see below)              |

---

## nearest_neighbor_settings Fields

Applies to both `supabase_metadata` and `pinecone_metadata`.

| Field                          | Type    | Default | Description                                                    |
| ------------------------------ | ------- | ------- | -------------------------------------------------------------- |
| get_all_neighbor_chunks        | boolean | `false` | Whether to fetch surrounding chunks around each result         |
| nearest_chunks_n               | integer | `0`     | Number of adjacent chunks to include on each side              |
| nearest_page_or_array_members_n| integer | `0`     | Number of adjacent page or array members to include            |

---

## Example Request

```bash
curl -X POST http://localhost:8000/chatbot/call_chatbot/ \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-H "Content-Type: application/json" \
-d '{
    "question": "What is Retrieval Augmented Generation?"
}'
```

---

## Success Response

Status: `200 OK`

```json
{
  "status": "success",
  "response": "Retrieval-Augmented Generation (RAG) combines information retrieval with large language models...",
  "classifer": "general_question",
  "conv_id": "d8f69ca9-54ef-43db-8b64-fd67a2d3f95a"
}
```

---

## Error Responses

### Authentication Error

```json
{
  "status": "error",
  "message": "Authentication ID is missing."
}
```

Status: `401 Unauthorized`

---

### Missing User API Keys

```json
{
  "status": "error",
  "message": "No API keys found for the provided user ID."
}
```

Status: `404 Not Found`

---

### Invalid JSON

```json
{
  "status": "error",
  "message": "Invalid JSON payload"
}
```

Status: `400 Bad Request`

---

# Conversation Memory

The chatbot automatically stores chat history.

### First Request

```json
{
  "question": "What is LangGraph?"
}
```

Response:

```json
{
  "conv_id": "12345-abcde"
}
```

### Continue Conversation

```json
{
  "question": "Can you show me an example?",
  "conv_id": "12345-abcde"
}
```

The chatbot loads previous messages and continues the conversation contextually.

---

# AI Processing Pipeline

Every request passes through the following workflow:

```text
Load Conversation Memory
          ↓
Fetch Context (Supabase / Pinecone)
          ↓
Classify User Query
          ↓
Check Prompt Injection
          ↓
Check Message Limits
          ↓
(Optional) Real-Time Knowledge Search
          ↓
(Optional) Contact Information Extraction
          ↓
Generate Final Response
          ↓
Store Conversation
          ↓
Return Response
```

---

# Context Retrieval (`fetch_context`)

Before generating a response, the pipeline optionally retrieves relevant context from one or both of the supported vector stores: **Supabase** and **Pinecone**. This is controlled by the `supabase_metadata` and `pinecone_metadata` fields in the request body.

If both are provided, each store is queried independently and the retrieved context is made available to the response generation step.

## Supabase Retrieval

When `supabase_metadata` is present, the system performs a vector search against the specified Supabase table. Supported retrieval modes are `semantic`, `keyword`, and `hybrid`. The similarity metric for semantic search is configurable via `semantic_search_mode` (`cosine`, `l2`, or `ip`).

## Pinecone Retrieval

When `pinecone_metadata` is present, the system queries the specified Pinecone index. For hybrid search, an optional `index_name_lexical` field can point to a secondary lexical index. The user's API keys are forwarded automatically.

## Chunk Expansion

Both retrieval paths support `nearest_neighbor_settings` to expand results beyond the top-k matches by pulling in surrounding chunks. This is useful when documents are split into small fragments and surrounding context improves answer quality.

```json
"nearest_neighbor_settings": {
  "get_all_neighbor_chunks": true,
  "nearest_chunks_n": 2,
  "nearest_page_or_array_members_n": 1
}
```

Setting `get_all_neighbor_chunks` to `true` activates expansion. `nearest_chunks_n` controls how many adjacent chunks are included, and `nearest_page_or_array_members_n` controls how many adjacent page or array-level members are fetched.

---

# Query Classification

The chatbot automatically classifies user messages.

| Classification      | Purpose                            |
| ------------------- | ---------------------------------- |
| general_question    | Standard Q&A                       |
| real_time_knowledge | Current events or live information |
| contact_flow        | Extract contact details            |
| forbidden_injection | Prompt injection attempts          |

Example:

```json
{
  "classifer": "real_time_knowledge"
}
```

---

# Real-Time Knowledge Search

For queries requiring current information, the chatbot can perform Google Search grounding through Gemini.

Example:

```json
{
  "question": "Who won the latest Formula 1 race?"
}
```

The system:

1. Detects real-time intent.
2. Executes Google Search grounding.
3. Injects search results into the response context.
4. Generates a grounded answer.

---

# Contact Information Extraction

The chatbot supports extracting structured contact information.

Example:

```json
{
  "question": "My name is John Doe, my email is john@example.com and my phone number is +1 555-1234."
}
```

The Contact Flow Agent processes the request and extracts relevant details.

---

# Conversation Limits

## Messages Per Conversation

```json
{
  "number_of_messages_per_conversation": 50
}
```

If exceeded:

```json
{
  "message": "You have exceeded the maximum number of messages allowed in this conversation."
}
```

Status: `429 Too Many Requests`

---

## Message Length Limit

```json
{
  "number_of_characters_per_message": 5000
}
```

If exceeded:

```json
{
  "message": "Your message exceeds the maximum character limit."
}
```

Status: `413 Payload Too Large`

---

# Supported LLM Providers

| Provider | Required Key    |
| -------- | --------------- |
| Gemini   | gemini_api_key  |
| Groq     | groq_api_key    |
| Mistral  | mistral_api_key |

---

# LLM Fallback System

If the primary model fails, fallback models are tried in order.

```json
{
  "llm_model": "gemini-2.5-flash",
  "fallbacks": [
    "llama-3.3-70b",
    "mistral-large-latest"
  ]
}
```

```text
Primary Model
      ↓
Failure
      ↓
Fallback Model #1
      ↓
Failure
      ↓
Fallback Model #2
```

---

# Example Full Session

### Start Conversation

Request:

```json
{
  "question": "What is LangGraph?"
}
```

Response:

```json
{
  "status": "success",
  "response": "LangGraph is a framework for building stateful AI workflows...",
  "classifer": "general_question",
  "conv_id": "3c8dfd6f-6d57-48fc-b2a9-8d8e8f1a65e7"
}
```

### Continue with RAG Context

Request:

```json
{
  "question": "How does it compare to LangChain?",
  "conv_id": "3c8dfd6f-6d57-48fc-b2a9-8d8e8f1a65e7",
  "pinecone_metadata": {
    "index_name": "docs-index",
    "model": "text-embedding-3-small",
    "top_k": 3,
    "mode": "semantic"
  }
}
```

Response:

```json
{
  "status": "success",
  "response": "LangGraph extends LangChain by enabling graph-based execution...",
  "classifer": "general_question",
  "conv_id": "3c8dfd6f-6d57-48fc-b2a9-8d8e8f1a65e7"
}
```

---

# Security Features

* Authentication required
* Prompt Injection Detection
* Conversation Limits
* Character Limits
* Structured Logging
* User Activity Auditing
* API Key Isolation Per User
* Retry Logic
* Model Fallbacks
* Conversation Persistence

---

# Dependencies

* Django Async Views
* LangGraph
* LangChain
* Google Gemini
* Groq
* Mistral AI
* PostgreSQL / Django ORM
* Async Database Operations
* Google Search Grounding
* Supabase (pgvector)
* Pinecone
* Structured Logging
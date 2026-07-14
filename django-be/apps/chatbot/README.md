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
* Conversation history storage and retrieval

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

All endpoints below require authentication.

Authentication middleware attaches:

```python
request.auth_id
```

which identifies the authenticated user.

> **Note:** If `auth_id` is missing, the code raises an internal error which is caught by the generic exception handler. In practice this currently comes back as a **500** response (not 401), in the standard error envelope:
>
> ```json
> {
>   "res_status": "error",
>   "response": "Authentication ID is missing."
> }
> ```

---

# Response Envelope

**All endpoints share the same top-level response shape.** This differs from earlier versions of this document — the keys are `res_status` and `response`, not `status` and `message`.

**Success:**
```json
{
  "res_status": "success",
  "response": { }
}
```

**Error:**
```json
{
  "res_status": "error",
  "response": "Human readable error message"
}
```

The contents of `response` vary per endpoint and are documented below.

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
  "question": "Summarize the uploaded document.",
  "llm_model": "gemini-2.5-flash",
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
  "question": "What does the policy say about refunds?",
  "llm_model": "gemini-2.5-flash",
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

| Field              | Type   | Required | Description                                                                 |
| ------------------ | ------ | -------- | ----------------------------------------------------------------------------|
| question           | string | Yes      | User message                                                                 |
| conv_id            | string | No       | Existing conversation ID                                                    |
| llm_model          | string | No*      | LLM model to use for the response, classifier, and other internal agents. `*` The code has no default — if omitted, `llm_model` is passed as `None` into the agent config and will likely cause a downstream failure. |
| supabase_metadata  | object | No       | Config for Supabase vector store retrieval                                  |
| pinecone_metadata  | object | No       | Config for Pinecone vector store retrieval                                  |

> Both `supabase_metadata` and `pinecone_metadata` are passed through `validate_metadata()` before use. Both may be omitted, and both may be provided together — each store is then queried independently.

---

## supabase_metadata Fields

| Field                    | Type    | Required | Default    | Description                                           |
| ------------------------ | ------- | -------- | ---------- | ----------------------------------------------------- |
| namespace                | string  | Yes      | —          | Namespace to scope the search                         |
| table_name               | string  | Yes      | —          | Supabase table to query                                |
| model                    | string  | Yes      | —          | Embedding model name                                   |
| top_k                    | integer | No       | `5`        | Number of top results to retrieve                      |
| mode                     | string  | No       | `semantic` | Retrieval mode: `semantic`, `keyword`, or `hybrid`     |
| semantic_search_mode     | string  | No       | `cosine`   | Similarity metric: `cosine`, `l2`, or `ip`             |
| nearest_neighbor_settings| object  | No       | `{}`       | Settings for chunk expansion (see below)               |

---

## pinecone_metadata Fields

| Field                    | Type    | Required | Default    | Description                                           |
| ------------------------ | ------- | -------- | ---------- | ----------------------------------------------------- |
| index_name               | string  | Yes      | —          | Primary Pinecone index name                            |
| index_name_lexical       | string  | No       | `null`     | Lexical index name for hybrid search                   |
| model                    | string  | Yes      | —          | Embedding model name                                   |
| top_k                    | integer | No       | `5`        | Number of top results to retrieve                      |
| mode                     | string  | No       | `semantic` | Retrieval mode: `semantic`, `keyword`, or `hybrid`     |
| nearest_neighbor_settings| object  | No       | `{}`       | Settings for chunk expansion (see below)               |

---

## nearest_neighbor_settings Fields

Applies to both `supabase_metadata` and `pinecone_metadata`.

| Field                          | Type    | Default | Description                                                    |
| ------------------------------ | ------- | ------- | -------------------------------------------------------------- |
| get_all_neighbor_chunks        | boolean | `false` | Whether to fetch surrounding chunks around each result          |
| nearest_chunks_n               | integer | `0`     | Number of adjacent chunks to include on each side                |
| nearest_page_or_array_members_n| integer | `0`     | Number of adjacent page or array members to include              |

---

## Example Request

```bash
curl -X POST http://localhost:8000/chatbot/call_chatbot/ \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-H "Content-Type: application/json" \
-d '{
    "question": "What is Retrieval Augmented Generation?",
    "llm_model": "gemini-2.5-flash"
}'
```

---

## Success Response

Status: `200 OK`

```json
{
  "res_status": "success",
  "response": {
    "response": "Retrieval-Augmented Generation (RAG) combines information retrieval with large language models...",
    "conv_id": "d8f69ca9-54ef-43db-8b64-fd67a2d3f95a"
  }
}
```

> **Note:** The `response` value is an object containing the answer text (itself under a nested `response` key) and `conv_id`. Earlier documentation showed a flat object with a top-level `classifer` field — the current endpoint code does not return `classifer` in the response payload, even though classification happens internally in the pipeline (see [Query Classification](#query-classification)).

---

## Error Responses

### Authentication Error

```json
{
  "res_status": "error",
  "response": "Authentication ID is missing."
}
```

Status: `500 Internal Server Error`

---

### Missing user_id

```json
{
  "res_status": "error",
  "response": "user_id is required"
}
```

Status: `400 Bad Request`

---

### Missing User API Keys

```json
{
  "res_status": "error",
  "response": "No API keys found for the provided user ID."
}
```

Status: `404 Not Found`

---

### Invalid JSON

```json
{
  "res_status": "error",
  "response": "Invalid JSON payload"
}
```

Status: `400 Bad Request`

---

### Invalid Request Method

```json
{
  "res_status": "error",
  "response": "Invalid request method. Please use POST to send a message."
}
```

Status: `400 Bad Request`

---

### Unhandled / Other Errors

Any other exception raised while building or running the pipeline (including metadata validation failures from `validate_metadata()`) is caught and returned as:

```json
{
  "res_status": "error",
  "response": "<exception message>"
}
```

Status: `500 Internal Server Error`

---

# Conversation Memory

The chatbot automatically stores chat history.

### First Request

```json
{
  "question": "What is LangGraph?",
  "llm_model": "gemini-2.5-flash"
}
```

Response:

```json
{
  "res_status": "success",
  "response": {
    "response": "LangGraph is a framework for building stateful, graph-based AI workflows...",
    "conv_id": "12345-abcde"
  }
}
```

### Continue Conversation

```json
{
  "question": "Can you show me an example?",
  "conv_id": "12345-abcde",
  "llm_model": "gemini-2.5-flash"
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

The chatbot classifies user messages internally as part of the pipeline state (`classifier` in the LangGraph state).

| Classification      | Purpose                            |
| ------------------- | ----------------------------------- |
| general_question    | Standard Q&A                        |
| real_time_knowledge  | Current events or live information  |
| contact_flow        | Extract contact details             |
| forbidden_injection  | Prompt injection attempts           |

> **Note:** This classification is used internally to route the pipeline, but is **not currently included** in the `call_chatbot` API response payload.

---

# Real-Time Knowledge Search

For queries requiring current information, the chatbot can perform Google Search grounding through Gemini.

Example:

```json
{
  "question": "Who won the latest Formula 1 race?",
  "llm_model": "gemini-2.5-flash"
}
```

The system:

1. Detects real-time intent.
2. Executes Google Search grounding.
3. Injects search results into the response context.
4. Generates a grounded answer.

> Note: this agent is configured with `"enabled": False` by default in the current request config — see [LLM Fallback System / Agent Config](#llm-fallback-system) below.

---

# Contact Information Extraction

The chatbot supports extracting structured contact information.

Example:

```json
{
  "question": "My name is John Doe, my email is john@example.com and my phone number is +1 555-1234.",
  "llm_model": "gemini-2.5-flash"
}
```

The Contact Flow Agent processes the request and extracts relevant details. This agent is `"enabled": True` by default.

---

# Conversation Limits

Limits are enforced per-request via a hardcoded `call_config` block built server-side (they are **not** currently configurable from the request body):

```json
{
  "call_config": {
    "number_of_messages_per_conversation": 8,
    "number_of_characters_per_message": 200
  }
}
```

If the message-count limit is exceeded, or the message exceeds the character limit, the pipeline sets internal `limit_exceeded` / `limit_exceeded_message` state and the resulting answer/response will reflect that condition through the normal `call_chatbot` response envelope (`res_status` / `response`) rather than a distinct top-level shape.

---

# Supported LLM Providers

| Provider | Required Key    |
| -------- | --------------- |
| Gemini   | gemini_api_key  |
| Groq     | groq_api_key    |
| Mistral  | mistral_api_key |

---

# LLM Fallback System / Agent Config

Each internal agent (`agent_response`, `agent_classifier`, `agent_contact_flow`, `agent_real_time_knowledge_flow`) is configured server-side per request:

```json
{
  "temperature": 0.1,
  "retry": 3,
  "fallbacks": [],
  "llm_model": "<value of request's llm_model>",
  "thinking_budget": 0
}
```

> **Note:** `fallbacks` is currently hardcoded to an empty list for every agent in the code shown — a top-level `fallbacks` field in the request body (as shown in earlier drafts of this document) is **not** read or applied. If configurable fallback routing is intended, it isn't wired up yet in `call_info_chatbot`.

---

# Conversation History Endpoints

These endpoints let a client list a user's past conversations and fetch the full message history for one conversation.

## Get Conversation List

```http
GET /chatbot/get_history/
```

Returns a list of the authenticated user's conversations. Each entry's `name` is derived from the first stored message's `user` field.

### Success Response

Status: `200 OK`

```json
{
  "res_status": "success",
  "response": [
    {
      "id": 14,
      "name": "What is LangGraph?"
    },
    {
      "id": 9,
      "name": "Summarize the uploaded document."
    }
  ]
}
```

> Conversations with an empty or missing `history` array are silently skipped and will not appear in this list.

### Error Responses

Same envelope/pattern as above:

```json
{ "res_status": "error", "response": "Authentication ID is missing." }
```
Status: `500`

```json
{ "res_status": "error", "response": "user_id is required" }
```
Status: `400`

```json
{ "res_status": "error", "response": "Invalid request method. Please use GET to send a message." }
```
Status: `400`

```json
{ "res_status": "error", "response": "<exception message>" }
```
Status: `500`

---

## Get Conversation History

```http
GET /chatbot/get_conv_history/?conv_id=<conv_id>
```

Returns the full question/answer history for a single conversation, ordered oldest → newest.

### Query Parameters

| Parameter | Type   | Required | Description                              |
| --------- | ------ | -------- | ---------------------------------------- |
| conv_id   | string | Yes      | The conversation ID to fetch history for |

### Success Response

Status: `200 OK`

```json
{
  "res_status": "success",
  "response": [
    {
      "question": "What is LangGraph?",
      "answer": "LangGraph is a framework for building stateful, graph-based AI workflows...",
      "created_at": "2026-07-10T14:22:31.512Z"
    },
    {
      "question": "Can you show me an example?",
      "answer": "Sure — here's a simple LangGraph example...",
      "created_at": "2026-07-10T14:23:05.998Z"
    }
  ]
}
```

### Error Responses

```json
{ "res_status": "error", "response": "Authentication ID is missing." }
```
Status: `500`

```json
{ "res_status": "error", "response": "user_id is required" }
```
Status: `400`

```json
{ "res_status": "error", "response": "conv_id is required" }
```
Status: `400`

```json
{ "res_status": "error", "response": "Invalid request method. Please use GET to send a message." }
```
Status: `400`

```json
{ "res_status": "error", "response": "<exception message>" }
```
Status: `500`

---

# Example Full Session

### Start Conversation

Request:

```json
{
  "question": "What is LangGraph?",
  "llm_model": "gemini-2.5-flash"
}
```

Response:

```json
{
  "res_status": "success",
  "response": {
    "response": "LangGraph is a framework for building stateful AI workflows...",
    "conv_id": "3c8dfd6f-6d57-48fc-b2a9-8d8e8f1a65e7"
  }
}
```

### Continue with RAG Context

Request:

```json
{
  "question": "How does it compare to LangChain?",
  "conv_id": "3c8dfd6f-6d57-48fc-b2a9-8d8e8f1a65e7",
  "llm_model": "gemini-2.5-flash",
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
  "res_status": "success",
  "response": {
    "response": "LangGraph extends LangChain by enabling graph-based execution...",
    "conv_id": "3c8dfd6f-6d57-48fc-b2a9-8d8e8f1a65e7"
  }
}
```

### List Conversations

Request:

```http
GET /chatbot/get_history/
```

Response:

```json
{
  "res_status": "success",
  "response": [
    { "id": 1, "name": "What is LangGraph?" }
  ]
}
```

### Fetch a Conversation's Full History

Request:

```http
GET /chatbot/get_conv_history/?conv_id=3c8dfd6f-6d57-48fc-b2a9-8d8e8f1a65e7
```

Response:

```json
{
  "res_status": "success",
  "response": [
    {
      "question": "What is LangGraph?",
      "answer": "LangGraph is a framework for building stateful AI workflows...",
      "created_at": "2026-07-10T14:22:31.512Z"
    },
    {
      "question": "How does it compare to LangChain?",
      "answer": "LangGraph extends LangChain by enabling graph-based execution...",
      "created_at": "2026-07-10T14:23:40.221Z"
    }
  ]
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
* Model Fallbacks (config scaffolding present; not currently populated from the request — see note above)
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
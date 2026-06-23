# Chatbot API Documentation

## Overview

The Chatbot API provides an AI-powered conversational endpoint that supports:

* Multi-turn conversation memory
* Conversation persistence
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
  "question": "What is Retrieval Augmented Generation?"
}
```

### Existing Conversation

```json
{
  "question": "Can you give me an example?",
  "conv_id": "d8f69ca9-54ef-43db-8b64-fd67a2d3f95a"
}
```

---

## Request Parameters

| Field    | Type   | Required | Description              |
| -------- | ------ | -------- | ------------------------ |
| question | string | Yes      | User message             |
| conv_id  | string | No       | Existing conversation ID |

---

## Example Request

```bash
curl -X POST http://localhost:8000/chatbot/call_chatbot/ \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-H "Content-Type: application/json" \
-d '{
    "question":"What is Retrieval Augmented Generation?"
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

## Error Response

### Authentication Error

```json
{
  "status": "error",
  "message": "Authentication ID is missing."
}
```

Status:

```http
401 Unauthorized
```

---

### Missing User API Keys

```http
404 Not Found
```

```json
{
  "status": "error",
  "message": "No API keys found for the provided user ID."
}
```

---

### Invalid JSON

```json
{
  "status": "error",
  "message": "Invalid JSON payload"
}
```

Status:

```http
400 Bad Request
```

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

# Query Classification

The chatbot automatically classifies user messages.

Possible classifications include:

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

The system enforces configurable limits.

## Messages Per Conversation

Configured through:

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

Status:

```http
429 Too Many Requests
```

---

## Message Length Limit

Configured through:

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

Status:

```http
413 Payload Too Large
```

---

# Supported LLM Providers

The chatbot dynamically loads models using user-provided API keys.

Supported providers:

| Provider | Required Key    |
| -------- | --------------- |
| Gemini   | gemini_api_key  |
| Groq     | groq_api_key    |
| Mistral  | mistral_api_key |

---

# LLM Fallback System

If the primary model fails, fallback models can be automatically used.

Example:

```json
{
  "llm_model": "gemini-2.5-flash",
  "fallbacks": [
    "llama-3.3-70b",
    "mistral-large-latest"
  ]
}
```

Flow:

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

### Continue Conversation

Request:

```json
{
  "question": "How does it compare to LangChain?",
  "conv_id": "3c8dfd6f-6d57-48fc-b2a9-8d8e8f1a65e7"
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

Core technologies used:

* Django Async Views
* LangGraph
* LangChain
* Google Gemini
* Groq
* Mistral AI
* PostgreSQL / Django ORM
* Async Database Operations
* Google Search Grounding
* Structured Logging

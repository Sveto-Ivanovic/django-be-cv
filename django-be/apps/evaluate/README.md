# Evaluation API

This module provides RAG (Retrieval-Augmented Generation) pipeline evaluation endpoints. Given a set of questions (and optionally reference answers), it retrieves context from your vector store, generates answers using an LLM, then scores them across four metrics: **faithfulness**, **answer relevancy**, **answer correctness**, and **context recall**.

All endpoints are prefixed with `/evaluate/` and require authentication via `auth_id`.

---

## Endpoints

### 1. `POST /evaluate/call_eval_text/`

Run an evaluation by sending the test dataset as JSON in the request body.

**Rate limit:** 4 requests/minute per IP

**Request body** (`application/json`):

```json
{
  "testcase_name": "my_test_v1",
  "llm_model": "gpt-4o",
  "eval_model": "gpt-4o",
  "to_evaluate": [
    {
      "question": "What is the capital of France?",
      "reference_answer": "Paris"
    }
  ],
  "pinecone_metadata": {
    "index_name": "my-index",
    "model": "text-embedding-3-small",
    "top_k": 5,
    "mode": "semantic"
  },
  "nearest_neighbor_settings": {
    "get_all_neighbor_chunks": false,
    "nearest_chunks_n": 0,
    "nearest_page_or_array_members_n": 0
  }
}
```

`reference_answer` is optional — including it enables the `answer_correctness` metric.

You may use `supabase_metadata` instead of (or in addition to) `pinecone_metadata`:

```json
"supabase_metadata": {
  "namespace": "my-namespace",
  "table_name": "documents",
  "model": "text-embedding-3-small",
  "top_k": 5,
  "mode": "semantic",
  "semantic_search_mode": "cosine"
}
```

**Response:**

```json
{
  "status": "success",
  "response": "Successfully evaluated the dataset.",
  "aggregate": {
    "faithfulness": 0.87,
    "answer_relevancy": 0.91,
    "answer_correctness": 0.78,
    "context_recall": 0.83
  },
  "records": [
    {
      "user_input": "What is the capital of France?",
      "reference": "Paris",
      "retrieved_contexts": ["France is a country in Western Europe. Its capital is Paris..."],
      "response": "The capital of France is Paris.",
      "faithfulness": 1.0,
      "faithfulness_explanation": "The answer is fully supported by the retrieved context.",
      "answer_relevancy": 0.95,
      "answer_relevancy_explanation": "The response directly answers the question.",
      "answer_correctness": 1.0,
      "answer_correctness_explanation": "The answer matches the reference exactly.",
      "context_recall": 0.9,
      "context_recall_explanation": "The relevant context was retrieved."
    }
  ],
  "total": 1,
  "aggregate_id": "a1b2c3d4-..."
}
```

---

### 2. `POST /evaluate/call_eval_json/`

Same evaluation pipeline as above, but accepts the test dataset as an uploaded `.json` file (multipart form data).

**Rate limit:** 4 requests/minute per IP

**Request** (`multipart/form-data`):

| Field | Type | Required | Description |
|---|---|---|---|
| `to_evaluate` | File (.json) | Yes | JSON array of evaluation objects |
| `testcase_name` | string | No | Label for this test run |
| `llm_model` | string | Yes | Model used for answering questions |
| `eval_model` | string | Yes | Model used for scoring |
| `pinecone_metadata` | JSON string | Conditional | Pinecone config (required if not using supabase) |
| `supabase_metadata` | JSON string | Conditional | Supabase config (required if not using pinecone) |
| `nearest_neighbor_settings` | JSON string | No | Chunk neighbor settings |

Example `to_evaluate.json`:

```json
[
  {
    "question": "What is the boiling point of water?",
    "reference_answer": "100 degrees Celsius at sea level"
  },
  {
    "question": "Who wrote Hamlet?"
  }
]
```

Example `curl`:

```bash
curl -X POST https://your-domain.com/evaluate/call_eval_json/ \
  -H "Authorization: Bearer <token>" \
  -F "to_evaluate=@./test_cases.json" \
  -F "testcase_name=chemistry_test" \
  -F "llm_model=gpt-4o" \
  -F "eval_model=gpt-4o" \
  -F 'pinecone_metadata={"index_name":"science-index","model":"text-embedding-3-small","top_k":5,"mode":"semantic"}'
```

**Response:** Same structure as `call_eval_text`.

---

### 3. `GET /evaluate/get_eval_aggregates/`

Retrieve all aggregate evaluation results for the authenticated user.

**Rate limit:** 10 requests/minute per IP

**Response:**

```json
{
  "status": "success",
  "response": [
    {
      "id": "a1b2c3d4-...",
      "test_case_name": "my_test_v1",
      "qa_model_used": "gpt-4o",
      "validation_model_used": "gpt-4o",
      "aggregate_metadata": {
        "faithfulness": 0.87,
        "answer_relevancy": 0.91
      },
      "created_at": "2025-06-15T10:30:00Z",
      "number_of_testcases": 10
    }
  ]
}
```

---

### 4. `GET /evaluate/get_eval_testcases/?aggregate_id=<id>`

Retrieve the individual test case results for a specific aggregate evaluation run.

**Rate limit:** 10 requests/minute per IP

**Query parameter:** `aggregate_id` (required)

**Response:**

```json
{
  "status": "success",
  "response": [
    {
      "id": "...",
      "aggregate_id": "a1b2c3d4-...",
      "test_case_name": "my_test_v1",
      "user_input": "What is the capital of France?",
      "response": "The capital of France is Paris.",
      "reference": "Paris",
      "faithfulness": 1.0,
      "faithfulness_explanation": "The answer is fully supported by the context.",
      "answer_relevancy": 0.95,
      "answer_relevancy_explanation": "The response directly answers the question.",
      "answer_correctness": 1.0,
      "answer_correctness_explanation": "Matches the reference answer.",
      "context_recall": 0.9,
      "context_recall_explanation": "Relevant context was retrieved."
    }
  ]
}
```

---

### 5. `POST /evaluate/delete_eval_aggregate/`

Delete an aggregate evaluation run and its associated test cases.

> **Note:** The decorator declares `DELETE` but the view handles `POST` — send as POST.

**Rate limit:** 10 requests/minute per IP

**Request body** (`application/json`):

```json
{
  "aggregate_id": "a1b2c3d4-..."
}
```

**Response:**

```json
{
  "status": "success",
  "response": "Aggregate a1b2c3d4-... deleted successfully"
}
```

---

## Metrics

| Metric | Requires reference answer | Description |
|---|---|---|
| `faithfulness` | No | Whether the answer is grounded in the retrieved context |
| `answer_relevancy` | No | Whether the answer is relevant to the question |
| `context_recall` | No | Whether the retrieved context covered what was needed |
| `answer_correctness` | **Yes** | Whether the answer matches the reference answer |

Scores are floats between 0 and 1. Each metric also returns an `_explanation` field with the evaluator's reasoning.

---

## Error responses

All endpoints return errors in this shape:

```json
{
  "status": "error",
  "response": "Description of what went wrong."
}
```

Common status codes: `400` for bad input, `401` for unexpected server errors, `404` for not found.
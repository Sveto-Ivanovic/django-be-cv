# Vector Search API

Django-based REST API for managing vector embeddings across two backends: **Pinecone** (managed vector database) and **Supabase** (PostgreSQL-backed vector storage). All endpoints are rate-limited to **4 requests/minute per IP** and require authentication via `auth_id`.

All endpoints are prefixed with `/embed/`.

> **Note on response envelope:** Every endpoint wraps its payload in a top-level envelope of the form `{"res_status": "success" | "error", "response": <payload>}` — not `status`. A few endpoints (noted below) previously appeared to double-wrap this envelope; in the actual code they only wrap once, with the inner payload's fields spread directly under `response`.

---

## Authentication

Every endpoint reads `request.auth_id` from the incoming request (set by middleware). This is used to look up the user and decrypt their stored Pinecone API key via AES-256.

---

## Pinecone Endpoints

### `POST /embed/create_pinecone_index/`

Creates a new Pinecone vector index for the authenticated user.

**Request Body (JSON)**

```json
{
  "index_name": "my-index",
  "vector_size": 1536,
  "type_of_index": "dense"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `index_name` | string | Yes | Name for the new index |
| `vector_size` | integer | Yes | Dimensionality of the vectors |
| `type_of_index` | string | Yes | `"dense"` or `"sparse"` |

**Success Response**

The payload is an object containing the created index name — not a message string:

```json
{
  "res_status": "success",
  "response": {
    "index_name": "my-index"
  }
}
```

**Failure Response**

`res_status` is `"error"` (not `"failure"`). Note that this same message is returned both when the index name already exists **and** when `type_of_index` is neither `"dense"` nor `"sparse"` — the API does not currently distinguish the two cases in its response text:

```json
{
  "res_status": "error",
  "response": "Index name already exists, please select another one."
}
```

`Note: Supported vector_size values are 1536, 2048, and 3072, which map internally to the embedding models embed-v4.0, jina-embeddings-v4, and gemini-embedding-001 respectively. Any other value raises "Supported dimensions are 3072, 1536 and 2048."`

---

### `GET /embed/get_pinecone_indexes/`

Returns a list of all Pinecone indexes belonging to the authenticated user.

**Request**: No body or query params required.

**Success Response**

```json
{
  "res_status": "success",
  "response": [
    {
      "index_name": "my-index",
      "metric": "cosine",
      "vector_type": "dense",
      "dimension": 1536,
      "embed_model": "dense-manual"
    }
  ]
}
```

---

### `POST /embed/delete_pinecone_index/`

Deletes a Pinecone index and removes its associated metadata from the database.

**Request Body (JSON)**

```json
{
  "index_name": "my-index"
}
```

**Success Response**

The success message is a plain string built as `f"Sucessfully deleted index:{index_name}"` — note the typo (`Sucessfully`) and the missing space after the colon, both present in the actual code:

```json
{
  "res_status": "success",
  "response": "Sucessfully deleted index:my-index"
}
```

---

### `GET /embed/fetch_pinecone_index_data/`

Fetches all records from a given Pinecone index. Uses async batched fetching with a concurrency limit of 2 simultaneous requests. If the index doesn't exist for this user, it returns an empty list rather than an error.

**Query Parameters**

| Param | Type | Required | Description |
|---|---|---|---|
| `index_name` | string | Yes | Name of the index to fetch from |

**Example Request**

```
GET /embed/fetch_pinecone_index_data/?index_name=my-index
```

**Success Response**

```json
{
  "res_status": "success",
  "response": [
    {
      "id": "vec_001",
      "metadata": { "source": "doc.pdf", "page": 1 },
      "values": [0.12, 0.45, "..."]
    }
  ]
}
```

---

### `GET /embed/fetch_pinecone_index_record/`

Fetches a single record from a Pinecone index by its ID.

**Query Parameters**

| Param | Type | Required | Description |
|---|---|---|---|
| `index_name` | string | Yes | Name of the index |
| `record_id` | string | Yes | ID of the record to fetch |

**Example Request**

```
GET /embed/fetch_pinecone_index_record/?index_name=my-index&record_id=vec_001
```

**Success Response**

```json
{
  "res_status": "success",
  "response": {
    "metadata": { "source": "doc.pdf", "page": 1 },
    "vector": [0.12, 0.45, 0.89, "..."],
    "id": "vec_001"
  }
}
```

---

### `POST /embed/delete_pinecone_index_record/`

Deletes one or more records from a Pinecone index by ID and updates the row count in metadata.

**Request Body (JSON)**

```json
{
  "index_name": "my-index",
  "record_id": ["vec_001", "vec_002"]
}
```

`record_id` can be a single string or a list of strings; a single string is normalized into a one-item list internally.

**Success Response**

The message embeds the Python list representation of the deleted IDs:

```json
{
  "res_status": "success",
  "response": "Successfully deleted record with id: ['vec_001', 'vec_002']"
}
```

---

### `POST /embed/create_textsearch_index/`

Creates a Pinecone text search (sparse/integrated) index.

**Request Body (JSON)**

```json
{
  "index_name": "my-text-index"
}
```

**Success Response**

```json
{
  "res_status": "success",
  "response": { }
}
```

*(The exact shape of `response` here depends on `create_pinecone_textsearch_index`, which isn't part of the provided source — treat this as a placeholder.)*

---

### `POST /embed/delete_textsearch_index/`

Deletes a Pinecone text search index. (In the provided source, this view is named `delete_pinecone_text_search`.)

**Request Body (JSON)**

```json
{
  "index_name": "my-text-index"
}
```

**Success Response**

```json
{
  "res_status": "success",
  "response": { }
}
```

*(Same caveat as above — depends on `delete_textsearch_index`, not included in the provided source.)*

---

## Supabase (PostgreSQL) Endpoints

Vectors are stored in one of three Django models depending on their dimensionality:

| Model | Table | Dimensions |
|---|---|---|
| `VectorSearch1536` | `vector_search_1536` | 1536 |
| `VectorSearch2048` | `vector_search_2048` | 2048 |
| `VectorSearch3072` | `vector_search_3072` | 3072 |

---

### `GET /embed/get_supabase_tables/`

Returns metadata about all Supabase vector namespaces owned by the authenticated user.

**Request**: No body or query params required.

**Success Response**

```json
{
  "res_status": "success",
  "response": [
    {
      "namespace": "my-namespace",
      "model": "text-embedding-3-small",
      "row_count": 42,
      "additional_info": null,
      "updated_at": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-10T08:00:00Z",
      "supabase_table_name": "vector_search_1536"
    }
  ]
}
```

---

### `GET /embed/list_supabase_table_records/`

Lists all records in a given Supabase vector table and namespace.

**Query Parameters**

| Param | Type | Required | Description |
|---|---|---|---|
| `table_name` | string | Yes | One of `vector_search_1536`, `vector_search_2048`, `vector_search_3072` |
| `namespace` | string | Yes | Namespace to filter by |

**Example Request**

```
GET /embed/list_supabase_table_records/?table_name=vector_search_1536&namespace=my-namespace
```

**Success Response**

The envelope wraps only **once** (not twice as previously documented), and the record list lives under the key `records`, not `response`:

```json
{
  "res_status": "success",
  "response": {
    "records": [
      {
        "id": "a1b2c3",
        "namespace": "my-namespace",
        "source": "report.pdf",
        "metadata": { "page": 2 },
        "created_at": "2024-01-12T09:00:00Z",
        "model": "text-embedding-3-small",
        "content": "This is the chunked text content...",
        "is_chunk": true,
        "chunk_number": 1,
        "type": "document"
      }
    ],
    "count": 1,
    "table_name": "vector_search_1536",
    "namespace": "my-namespace"
  }
}
```

---

### `POST /embed/delete_supabase_records/`

Deletes specific records from a Supabase vector table by their IDs and updates the namespace row count.

**Request Body (JSON)**

```json
{
  "table_name": "vector_search_1536",
  "namespace": "my-namespace",
  "ids": ["a1b2c3", "d4e5f6"]
}
```

**Success Response**

Single-level envelope; the payload uses `message` (not `response`) for the human-readable text, plus a numeric `delete_count`:

```json
{
  "res_status": "success",
  "response": {
    "message": "Successfully deleted 2 records from vector_search_1536 for user 99",
    "delete_count": 2,
    "details": { "apps.vector_search.embed1536": 2 }
  }
}
```

---

### `POST /embed/delete_supabase_namespace/`

Deletes an entire namespace and all its records from a Supabase table, and removes the namespace entry from `UserVectorMetadata`.

**Request Body (JSON)**

```json
{
  "namespace": "my-namespace",
  "table_name": "vector_search_1536"
}
```

**Success Response**

Single-level envelope; payload includes `message`, `namespace`, `table_name`, and `delete_count`:

```json
{
  "res_status": "success",
  "response": {
    "message": "Successfully deleted namespace my-namespace and all associated records from vector_search_1536 for user 99",
    "namespace": "my-namespace",
    "table_name": "vector_search_1536",
    "delete_count": 7
  }
}
```

---

## Embed Endpoints

These endpoints are registered but defined in `views_embed` (not shown in the provided source).

| Method | URL | Description |
|---|---|---|
| POST | `/embed/embed_items_into_pinecone/` | Embed and upsert items into a Pinecone index |
| POST | `/embed/embed_items_into_supabase/` | Embed and insert items into a Supabase vector table |

---

## Error Responses

All endpoints return consistent error shapes:

```json
{
  "res_status": "error",
  "response": "Description of what went wrong"
}
```

| HTTP Status | Meaning |
|---|---|
| `400` | Invalid JSON payload, missing required field, missing auth ID, or missing Pinecone API key |
| `429` | Rate limit exceeded (4 requests/minute per IP) |
| `500` | Unhandled exception, or (for Pinecone-backed views only) an unsupported HTTP method |
| `405` | Unsupported HTTP method — Supabase-backed views (`get_supabase_tables`, `delete_supabase_records`, `list_supabase_table_records`, `delete_supabase_namespace`) return this; Pinecone-backed views return `500` instead for the same case |

There is no `401` status used anywhere in the provided source — auth/key failures are surfaced as `400`.
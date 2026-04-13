# Pinecone & Supabase Embedding Endpoints 🚀

This document outlines how to use the universal embedding endpoints to process and upsert text, images, and documents into [Pinecone](https://www.pinecone.io/) vector indexes or Supabase vector tables.

### Note: user_id now needs to be provided in the request body for both Pinecone and Supabase embedding endpoints. This allows the system to retrieve the appropriate API keys for the user making the request.

---

## Available Endpoints

- **Pinecone**: `/embed/embed_items_into_pinecone/`
- **Supabase**: `/embed/embed_items_into_supabase/`

---

## Core Parameters

These are the main fields for every request.

### Pinecone-Specific Parameters

* `pinecone_api_key` (string, **required**): Your Pinecone API key.
* `index_name` (string, **required**): The name of your target Pinecone index.

### Supabase-Specific Parameters

* `table_name` (string, **required**): The name of your target Supabase table. Must be one of the supported tables:
  - `vector_search_1536` - For 1536-dimensional embeddings (Cohere embed-v4.0)
  - `vector_search_2048` - For 2048-dimensional embeddings (Jina jina-embeddings-v4)
  - `vector_search_3072` - For 3072-dimensional embeddings (Gemini gemini-embedding-001)

### Common Parameters (Both Endpoints)

* `embed_model` (string, **required**): The embedding model to use. See the available models below.
* `input_mode` (string, **required**): Specifies the type of input. Can be `text`, `image`, or `file`.
* `data` (array, **required**): The input data to embed. The structure depends on the `input_mode`.
* `input_metadata` (array, **optional**): Metadata to apply to the embeddings. This can be an empty array `[]`, an array with a single object to apply to all embeddings, or an array of objects where each object corresponds to an item in the `data` array.
* `chunk_config` (object, **optional**): Configuration for splitting text into smaller chunks. Contains `chunk_size` (integer) and `overlap` (integer).
* `include_image_embedding` (boolean, **optional**): Only applicable for `file` input mode. If `true`, images within the files will also be embedded. Defaults to `false`.

---

## Embedding Models

### Pinecone
The chosen embedding model's dimensions **must match** the dimension of your Pinecone dense index.

### Supabase
The chosen embedding model **must match** the table dimensions as follows:

| Model Name               | Dimensions | Supabase Table          | Supported Input         | Notes                                                               |
| ------------------------ | ---------- | ----------------------- | ----------------------- | ------------------------------------------------------------------- |
| `gemini-embedding-001`   | `3072`     | `vector_search_3072`    | Text                    | Can only be used for text-based inputs.                             |
| `jina-embeddings-v4`     | `2048`     | `vector_search_2048`    | Text, Image             | Multimodal model suitable for both text and image data.             |
| `embed-v4.0`             | `1536`     | `vector_search_1536`    | Text, Image             | Multimodal model suitable for both text and image data.             |

⚠️ **Important**: 
- For Supabase, you must use the correct table for your chosen model
- When using `input_mode: "file"`, the `gemini-embedding-001` model can only be used if `include_image_embedding` is set to `false`

---

## Usage Modes & Examples

### 📝 Mode: `text`

Use this mode for embedding raw text strings.

#### Example 1: Simple Text Array (Supabase)

```json
{
    "table_name": "vector_search_3072",
    "embed_model": "gemini-embedding-001",
    "input_mode": "text",
    "input_metadata": [],
    "data": [
        "Time is one of the most valuable resources we have, yet it often slips through our fingers unnoticed.",
        "Growth doesn't happen in dramatic leaps every day. More often, it's the small, consistent efforts that shape who we become."
    ]
}
```

#### Example 2: Simple Text Array (Pinecone)

```json
{
    "pinecone_api_key": "YOUR_PINECONE_API_KEY",
    "index_name": "knowledge-base",
    "embed_model": "gemini-embedding-001",
    "input_mode": "text",
    "input_metadata": [],
    "data": [
        "Time is one of the most valuable resources we have, yet it often slips through our fingers unnoticed.",
        "Growth doesn't happen in dramatic leaps every day. More often, it's the small, consistent efforts that shape who we become."
    ]
}
```

#### Example 3: Shared Metadata

A single metadata object in `input_metadata` is applied to all generated embeddings.

**Supabase:**
```json
{
    "table_name": "vector_search_3072",
    "embed_model": "gemini-embedding-001",
    "input_mode": "text",
    "input_metadata": [{
        "source": "philosophy-weekly"
    }],
    "data": [
        "Time is one of the most valuable resources we have...",
        "Growth doesn't happen in dramatic leaps every day..."
    ]
}
```

**Pinecone:**
```json
{
    "pinecone_api_key": "YOUR_PINECONE_API_KEY",
    "index_name": "knowledge-base",
    "embed_model": "gemini-embedding-001",
    "input_mode": "text",
    "input_metadata": [{
        "source": "philosophy-weekly"
    }],
    "data": [
        "Time is one of the most valuable resources we have...",
        "Growth doesn't happen in dramatic leaps every day..."
    ]
}
```

#### Example 4: Individual Metadata per Item

Provide a metadata object for each corresponding item in the `data` array.

**Supabase:**
```json
{
    "table_name": "vector_search_2048",
    "embed_model": "jina-embeddings-v4",
    "input_mode": "text",
    "input_metadata": [
        { "doc_id": "essay-on-time" },
        { "doc_id": "notes-on-growth", "author": "J. Smith" }
    ],
    "data": [
        "Time is one of the most valuable resources we have...",
        "Growth doesn't happen in dramatic leaps every day..."
    ]
}
```

#### Example 5: Data as JSON Objects

You can also provide data as an array of objects, each containing `text` and an optional `metadata` key.

**Supabase:**
```json
{
    "table_name": "vector_search_1536",
    "embed_model": "embed-v4.0",
    "input_mode": "text",
    "input_metadata": [],
    "data": [{
        "text": "Time is one of the most valuable resources we have...",
        "metadata": {
            "source": "internal-docs",
            "id": "doc-alpha-001"
        }
    }, {
        "text": "Growth doesn't happen in dramatic leaps every day...",
        "metadata": {
            "source": "public-blog",
            "id": "post-beta-002"
        }
    }]
}
```

#### Example 6: Text with Chunking

Use `chunk_config` to automatically split long texts. Metadata is applied to each chunk derived from the source text.

**Supabase:**
```json
{
    "table_name": "vector_search_3072",
    "embed_model": "gemini-embedding-001",
    "input_mode": "text",
    "input_metadata": [],
    "data": [
        "Time is one of the most valuable resources we have, yet it often slips through our fingers unnoticed. We spend days chasing deadlines, obligations, distractions—only to look back and wonder where the time went...",
        "Growth doesn't happen in dramatic leaps every day. More often, it's the small, consistent efforts that shape who we become. It's in the books we read, the conversations we engage in, the mistakes we learn from..."
    ],
    "chunk_config": {
        "chunk_size": 100,
        "overlap": 50
    }
}
```

---

### 🖼️ Mode: `image`

Use this mode to embed images from URLs or by uploading local files. **Cannot be used with `gemini-embedding-001`**.

#### Example 1: Image URLs (Supabase)

The `data` array should contain objects with a `url` key. You can also include `metadata` inside these objects.

```json
{
    "table_name": "vector_search_2048",
    "embed_model": "jina-embeddings-v4",
    "input_mode": "image",
    "input_metadata": [],
    "data": [
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Logo_Alouen_Version_Finale_PNG_400x400.png",
            "metadata": { "category": "brand-assets" }
        },
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/9/9a/Connective_Logo_400x400.png",
            "metadata": { "category": "partner-logos" }
        }
    ]
}
```

#### Example 2: Uploading Local Images (Supabase)

To upload local files, send a `multipart/form-data` request. The JSON payload is sent as one part, and the image files are sent as subsequent parts.

**Request Body (form-data):**

* **`json` (text part):**
  ```json
  {
      "table_name": "vector_search_1536",
      "embed_model": "embed-v4.0",
      "input_mode": "image",
      "input_metadata": [
          { "event": "conference-2025" },
          { "event": "product-launch" }
      ]
  }
  ```
* **`files` (file part):** Select your image files (e.g., `image1.png`, `image2.jpg`). The number of files should match the number of objects in `input_metadata` if it's provided and not a single shared object.

---

### 📄 Mode: `file`

Use this mode for embedding documents like PDFs. This mode extracts text and, optionally, images from the files. Requests must be `multipart/form-data`.

#### Example 1: Files with Text & Image Embeddings (Supabase)

Set `include_image_embedding` to `true` to create embeddings for both the extracted text and any images within the files. Remember to use a multimodal model.

**Request Body (form-data):**

* **`json` (text part):**
  ```json
  {
      "table_name": "vector_search_2048",
      "embed_model": "jina-embeddings-v4",
      "input_mode": "file",
      "input_metadata": [],
      "include_image_embedding": true,
      "chunk_config": {"chunk_size": 1400, "overlap": 200}
  }
  ```
* **`files` (file part):** Select your document files (e.g., `report.pdf`, `spec-sheet.pdf`).

#### Example 2: Files with Text-Only Embeddings (Supabase)

Set `include_image_embedding` to `false` (or omit it) to only embed the extracted text. This allows you to use text-only models like `gemini-embedding-001`.

**Request Body (form-data):**

* **`json` (text part):**
  ```json
  {
      "table_name": "vector_search_3072",
      "embed_model": "gemini-embedding-001",
      "input_mode": "file",
      "input_metadata": [{ "source": "annual-reports" }],
      "include_image_embedding": false
  }
  ```
* **`files` (file part):** Select your document file(s) (e.g., `annual-report-2024.pdf`).

---

## Quick Reference

### When to use Pinecone vs Supabase

**Use Pinecone when:**
- You need a dedicated vector database with custom index configurations
- You want full control over index dimensions and specifications
- You require Pinecone's specific features and optimizations

**Use Supabase when:**
- You want to use predefined tables with standard dimensions
- You prefer a simpler setup with fixed table structures
- You're already using Supabase for other data storage needs

### Table/Model Compatibility Matrix

| Embed Model             | Pinecone             | Supabase Table          |
| ----------------------- | -------------------- | ----------------------- |
| `gemini-embedding-001`  | 3072-dim index       | `vector_search_3072`    |
| `jina-embeddings-v4`    | 2048-dim index       | `vector_search_2048`    |
| `embed-v4.0`            | 1536-dim index       | `vector_search_1536`    |
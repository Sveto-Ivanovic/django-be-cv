# Embed App Endpoints

This document provides a detailed description of the API endpoints available in the `embed` app. These endpoints are used for managing Pinecone indexes and embedding data.

## Base URL

All endpoints are prefixed with `/embed/`.

---

## Pinecone Index Management

### 1. Create Pinecone Index

-   **Endpoint:** `POST /embed/create_pinecone_index/`
-   **Description:** Creates a new serverless vector index in Pinecone.
-   **Request Body (`application/json`):**
    ```json
    {
        "pinecone_api_key": "YOUR_PINECONE_API_KEY",
        "index_name": "my-new-index",
        "vector_size": 1536,
        "type_of_index": "dense"
    }
    ```
    -   `pinecone_api_key` (string, optional): Your Pinecone API key. If not provided, it will be read from the environment variable `PINECONE_API_KEY`.
    -   `index_name` (string, required): The desired name for the new index.
    -   `vector_size` (integer, required): The dimension of the vectors to be stored in the index.
    -   `type_of_index` (string, required): The type of index to create. Can be `"dense"` or `"sparse"`.
-   **Responses:**
    -   **200 OK (Success):**
        ```json
        {
            "status": "sucess",
            "response": "Sucessfully created index: my-new-index"
        }
        ```
    -   **401 Unauthorized (Failure/Error):**
        ```json
        {
            "status": "failure",
            "response": "Index name already exists, please select another one."
        }
        ```

### 2. Get Pinecone Indexes

-   **Endpoint:** `GET /embed/get_pinecone_indexes/`
-   **Description:** Retrieves a list of all available Pinecone indexes.
-   **Query Parameters:**
    -   `pinecone_api_key` (string, optional): Your Pinecone API key.
-   **Responses:**
    -   **200 OK (Success):**
        ```json
        {
            "status": "sucess",
            "response": [
                {
                    "index_name": "my-index",
                    "metric": "cosine",
                    "vector_type": "dense",
                    "dimension": 1536,
                    "embed_model": "text-embedding-ada-002"
                }
            ]
        }
        ```
    -   **401 Unauthorized (Error):**
        ```json
        {
            "status": "error",
            "response": "Error message details."
        }
        ```

### 3. Delete Pinecone Index

-   **Endpoint:** `POST /embed/delete_pinecone_index/`
-   **Description:** Deletes a specified Pinecone index.
-   **Request Body (`application/json`):**
    ```json
    {
        "pinecone_api_key": "YOUR_PINECONE_API_KEY",
        "index_name": "index-to-delete"
    }
    ```
    -   `pinecone_api_key` (string, optional): Your Pinecone API key.
    -   `index_name` (string, required): The name of the index to delete.
-   **Responses:**
    -   **200 OK (Success):**
        ```json
        {
            "status": "sucess",
            "response": "Sucessfully deleted index:index-to-delete"
        }
        ```
    -   **401 Unauthorized (Error):**
        ```json
        {
            "status": "error",
            "response": "Error message details."
        }
        ```

---

## Pinecone Record Management

### 4. Fetch All Records from a Pinecone Index

-   **Endpoint:** `POST /embed/fetch_pinecone_index_data/`
-   **Description:** Asynchronously fetches all records (vectors and metadata) from a specified index.
-   **Request Body (`application/json`):**
    ```json
    {
        "pinecone_api_key": "YOUR_PINECONE_API_KEY",
        "index_name": "my-index"
    }
    ```
-   **Responses:**
    -   **200 OK (Success):**
        ```json
        {
            "status": "sucess",
            "response": [
                {
                    "id": "record-1",
                    "metadata": { "key": "value" },
                    "vector": [0.1, 0.2, ...]
                }
            ]
        }
        ```
    -   **401 Unauthorized (Error):**
        ```json
        {
            "status": "error",
            "response": "Error message details."
        }
        ```

### 5. Fetch a Single Record from a Pinecone Index

-   **Endpoint:** `GET /embed/fetch_pinecone_index_record/`
-   **Description:** Fetches a single record by its ID from a specified index.
-   **Query Parameters:**
    -   `pinecone_api_key` (string, optional): Your Pinecone API key.
    -   `index_name` (string, required): The name of the index.
    -   `record_id` (string, required): The ID of the record to fetch.
-   **Responses:**
    -   **200 OK (Success):**
        ```json
        {
            "status": "sucess",
            "response": {
                "id": "record-1",
                "metadata": { "key": "value" },
                "vector": [0.1, 0.2, ...]
            }
        }
        ```
    -   **401 Unauthorized (Error):**
        ```json
        {
            "status": "error",
            "response": "Error message details."
        }
        ```

### 6. Delete Record(s) from a Pinecone Index

-   **Endpoint:** `POST /embed/delete_pinecone_index_record/`
-   **Description:** Deletes one or more records from a specified index.
-   **Request Body (`application/json`):**
    ```json
    {
        "pinecone_api_key": "YOUR_PINECONE_API_KEY",
        "index_name": "my-index",
        "record_id": ["record-1", "record-2"]
    }
    ```
    -   `record_id` (string or array of strings, required): The ID(s) of the record(s) to delete.
-   **Responses:**
    -   **200 OK (Success):**
        ```json
        {
            "status": "sucess",
            "response": "Sucessfully deleted record with id: ['record-1', 'record-2']"
        }
        ```
    -   **401 Unauthorized (Error):**
        ```json
        {
            "status": "error",
            "response": "Error message details."
        }
        ```

---

## Data Embedding

### 7. Embed and Upsert Items into Pinecone

-   **Endpoint:** `POST /embed/embed_items_into_pinecone/`
-   **Description:** A universal endpoint to embed text, images, or files and upsert them into a Pinecone index. This endpoint supports various input modes and configurations. For detailed usage and examples for each mode (`text`, `image`, `file`), please refer to the [Input Types and Examples for Embed Endpoints](./views/README.md).
-   **Request Body (`application/json` or `multipart/form-data`):**
    -   The request body is complex and depends on the `input_mode`. See the detailed documentation for examples.
-   **Responses:**
    -   **200 OK (Success):** The response format varies based on the operation but generally indicates success.
        ```json
        {
            "status": "success",
            "response": "Successfully embedded and upserted X items."
        }
        ```
    -   **400 Bad Request / 401 Unauthorized (Error):**
        ```json
        {
            "status": "error",
            "response": "Error message details."
        }
        ```

import json
import os
import time
from pinecone import Pinecone
from pinecone.preview import SchemaBuilder
import copy


def create_pinecone_textsearch_index(
    pinecone_index_name: str, 
    pinecone_api_key: str
):
    """
    Create a Pinecone index for text search.
    Args:
        pinecone_index_name (str): The name of the Pinecone index to create.
        pinecone_api_key (str): The API key for accessing Pinecone.
    Returns:
        dict: A dictionary containing the status and details of the index creation process.
    """
    pc = Pinecone(api_key=pinecone_api_key)

    if pc.has_index(pinecone_index_name):
        raise ValueError(f"Index '{pinecone_index_name}' already exists.")
    
    schema = (
    SchemaBuilder()
      .add_string_field(name="text", full_text_search={"language": "en"})
      .build()
    )

    pc.preview.indexes.create(name=pinecone_index_name, schema=schema)

    # Wait for the index to be ready before upserting (no timeout — add a loop cap in production).
    while not pc.preview.indexes.describe(name=pinecone_index_name).status.ready:
        time.sleep(2)

    return {"status": "success", "message": f"Index '{pinecone_index_name}' created successfully."}


def delete_textsearch_index(
    pinecone_index_name: str, 
    pinecone_api_key: str
):
    """
    Delete a Pinecone index.
    Args:
        pinecone_index_name (str): The name of the Pinecone index to delete.
        pinecone_api_key (str): The API key for accessing Pinecone.
    Returns:
        dict: A dictionary containing the status and details of the index deletion process.
    """
    pc = Pinecone(api_key=pinecone_api_key)

    if not pc.has_index(pinecone_index_name):
        raise ValueError(f"Index '{pinecone_index_name}' does not exist.")
    
    pc.preview.indexes.delete(name=pinecone_index_name)

    return {"status": "success", "message": f"Index '{pinecone_index_name}' deleted successfully."}


def upsert_textsearch_index(
    pinecone_index_name: str, 
    records: list, 
    pinecone_api_key: str
):
    """
    Upsert records into a Pinecone index.
    Args:
        pinecone_index_name (str): The name of the Pinecone index to upsert into.
        records (list): A list of dictionaries representing the records to upsert. Each dictionary should have a 'text' key.
        pinecone_api_key (str): The API key for accessing Pinecone.
    Returns:
        dict: A dictionary containing the status and details of the upsert process.
    """
    pc = Pinecone(api_key=pinecone_api_key)
    records = copy.deepcopy(records)

    if not pc.has_index(pinecone_index_name):
        raise ValueError(f"Index '{pinecone_index_name}' does not exist.")
    
    index = pc.preview.index(name=pinecone_index_name)

    # Upsert records (each record must have a unique ID; here we use the index in the list as the ID).
    updated_records = []

    for record in records:

        if record.get("metadata", {}).get("text", None) is None:
            continue
        else:
            record["text"]=record.get("metadata", {}).get("text", None)

        if "_id" not in record:
            record["_id"] = str(record.get("id", time.time()))  
            record.pop("id", None)
        record["metadata"] = json.dumps(record.get("metadata", {}))  
        record.pop("values", None)
        updated_records.append(record)

    print(updated_records[1:2])


    index.documents.upsert(
        namespace="default",
        documents=updated_records
    )

    return {"status": "success", "message": f"{len(records)} records upserted into index '{pinecone_index_name}' successfully."}


def query_textsearch_index(
    pinecone_index_name: str, 
    query: str, 
    pinecone_api_key: str, 
    top_k: int = 5
):
    """
    Query a Pinecone index for text search.
    Args:
        pinecone_index_name (str): The name of the Pinecone index to query.
        query (str): The search query.
        pinecone_api_key (str): The API key for accessing Pinecone.
        top_k (int, optional): The number of top results to return. Defaults to 5.
    Returns:
        dict: A dictionary containing the status and search results.
    """
    pc = Pinecone(api_key=pinecone_api_key)

    if not pc.has_index(pinecone_index_name):
        raise ValueError(f"Index '{pinecone_index_name}' does not exist.")
    
    index = pc.preview.index(name=pinecone_index_name)

    print("yo")
    results = index.documents.search(
        namespace="default",
        top_k=top_k,
        score_by=[
            {
                "type": "text",
                "field" : "text",
                "query": query
            }
        ],
        include_fields=["text","metadata"]
    )

    matches = [
    {
        "id": match._id,
        "lexical_score": match.score,
        "metadata": json.loads(match.metadata) or {},
        "text": match.text

    }
    for match in results.matches
    ]

    return matches
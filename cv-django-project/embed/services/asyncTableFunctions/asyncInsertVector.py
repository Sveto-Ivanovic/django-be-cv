from asgiref.sync import sync_to_async
import logging
from ...models import VectorSearch1536, VectorSearch2048, VectorSearch3072
from django.utils import timezone

logger = logging.getLogger(__name__)

import uuid

def is_valid_uuid4(value: str) -> bool:
    try:
        u = uuid.UUID(value, version=4)
    except (ValueError, TypeError):
        return False
    return u.version == 4 and str(u) == value.lower()


@sync_to_async()
def async_insert_vector(table_name: str, vector_data: list):
    """Insert vector data into the specified table asynchronously.
        :param table_name: Name of the table to insert data into.
        :param vector_data: List of dictionaries containing vector data with keys 'id', 'values', and 'metadata'.
        
    """
    try:
        array = []

        for item in vector_data:
            
            id=item.get("id", None)
            if not is_valid_uuid4(id):
                id = id[0:36]
                if not is_valid_uuid4(id):
                    id = str(uuid.uuid4())
            


            vector=item.get("values", None)
            metadata=item.get("metadata", None)
            created_at = timezone.now()
            
            source = None
            model = None
            content = None
            is_chunk = False
            chunk_number = None
            type_of_flow = None
            print(metadata)

            if metadata:
                
                source = metadata.get("source") or metadata.get("file_type") or "unknown"
                model = metadata.get("embedding_model")
                content = metadata.get("text") or metadata.get("url")
                chunk_number = metadata.get("chunk_index")
                is_chunk = True if chunk_number is not None else False
                type_of_flow = metadata.get("type_of_flow") or "Unknown"

            if id is None or vector is None:
                raise ValueError("Each item in vector_data must contain 'id' and 'values' keys.")

            if table_name == "vector_search_1536":
                
                array.append(VectorSearch1536(
                    id=id,
                    source=source,
                    metadata=metadata,
                    created_at=created_at,
                    model=model,
                    content=content,
                    is_chunk=is_chunk,
                    chunk_number=chunk_number,
                    type=type_of_flow,
                    embedding=vector
                    ))
                
            elif table_name == "vector_search_2048":
                
                array.append(VectorSearch2048(
                    id=id,
                    source=source,
                    metadata=metadata,
                    created_at=created_at,
                    model=model,
                    content=content,
                    is_chunk=is_chunk,
                    chunk_number=chunk_number,
                    type=type_of_flow,
                    embedding=vector
                    ))
                
            elif table_name == "vector_search_3072":

                array.append(VectorSearch3072(
                    id=id,
                    source=source,
                    metadata=metadata,
                    created_at=created_at,
                    model=model,
                    content=content,
                    is_chunk=is_chunk,
                    chunk_number=chunk_number,
                    type=type_of_flow,
                    embedding=vector
                    ))
                
            else:
                raise ValueError(f"Invalid table name: {table_name}. Supported tables are vector_search_1536, vector_search_2048, vector_search_3072.")


        if array:
            if table_name == "vector_search_1536":
                VectorSearch1536.objects.bulk_create(array, batch_size=500)
            elif table_name == "vector_search_2048":
                VectorSearch2048.objects.bulk_create(array, batch_size=500)
            elif table_name == "vector_search_3072":
                VectorSearch3072.objects.bulk_create(array, batch_size=500)

    except Exception as e:
        logger.error(f"Error in async_insert_vector function: {str(e)}")
        raise

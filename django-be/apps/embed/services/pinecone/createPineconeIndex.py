from pinecone import ServerlessSpec
from ...loggerChatbot import logger

def create_pinecone(pc, type_of_index: str, index_name: str, vector_size: str):
    try:
        if type_of_index == "dense":
            pc.create_index(
                name=index_name,
                vector_type="dense",
                dimension=vector_size,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                ),
                deletion_protection="disabled",
                tags={
                    "environment": "development"
                }
            )
        elif type_of_index == "sparse":

            pc.create_index_for_model(
                name=index_name,
                cloud="aws",
                region="us-east-1",
                embed={
                    "model": "pinecone-sparse-english-v0",         
                    "field_map": {"text": "content"}          
                }
            )
    except Exception as e:
        logger.error(f"Error occured while creating pinecone index: {str(e)}")
        raise

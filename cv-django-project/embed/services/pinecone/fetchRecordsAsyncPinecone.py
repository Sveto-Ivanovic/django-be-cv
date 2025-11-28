import json
import time

from pinecone import Pinecone
from ...loggerChatbot import logger


def get_record_ids(index):
    record_idxs=[]
    for idx in index.list():
        record_idxs.extend(idx)
    return record_idxs


def batch_record_ids(record_idxs: list):
    """To call pinecone fetch api this process is necesssary for limits."""
    current_batch = []
    current_length = 2 

    # batch indexes to fetch their data
    batches = []
    for idx in record_idxs:
        id_len = len(json.dumps(idx)) + 1
        if current_length + id_len > 500:
            batches.append(current_batch)
            current_batch = []
            current_length = 2
        current_batch.append(idx)
        current_length += id_len
    if current_batch:
        batches.append(current_batch)
    
    return batches


def process_batch_record_results(batch_results):
    records=[]
    for batch_result in batch_results:
        vector_data = []
        for id,vector in batch_result.vectors.items():
            vector_data.append(
                {
                    'id': id,
                    #'vector': vector.values,
                    'metadata': vector.metadata
                }
            )

        records.extend(vector_data) 
    return records 

async def fetch_batch(index, batch: list, ind: int):
    logger.info(f"Starting fetch for batch:{ind}")
    res = await index.fetch(ids=batch)
    logger.info(f"Ending fetch for batch:{ind}")
    return res


def fetch_pinecone_ids(pinecone_api_key:str, index_name: str):
    start_time = time.time()
    pc = Pinecone(api_key=pinecone_api_key)
    index_description=pc.describe_index(name=index_name)
    index = pc.Index(name=index_name)
    logger.info(f"Time of exec. for pinecone index init and description:{time.time()- start_time}")

    # get vector indexes
    record_idxs= get_record_ids(index)

    return record_idxs, index_description.index.host
import  type{ NullLiteral } from "typescript";

export type CreatePineconeIndexRequest = {
    index_name: string;
    vector_size: number | string;
    type_of_index: "dense" | "sparse"
}

export type CreatePineconeIndexResponse = {
    index_name: string;
}


export type CreatePineconeIndexTextSearchRequest = {
    index_name: string;
}

export type CreatePineconeIndexTextSearchResponse = {
    status: string;
    message: string;
}

export type DeletePineconeIndexTextSearchRequest = {
    index_name: string;
}

export type DeletePineconeIndexTextSearchResponse = {
    status: string;
    message: string;
}

export type IndexItem = {
    index_name: string;
    metric: string;
    vector_type: string;
    dimension: number | null | undefined | NullLiteral;
    embed_model: string;
};

export type GetPineconeIndexesResponse = IndexItem[]


export type DeletePineconeIndexRequest = {
    index_name: string;
}


export type GetPineconeIndexRecordsRequest = {
    index_name: string;
}

export type PineconeIndexRecord = {
    id: string,
    index_name: string;
    source: string;
    chunk_number: number;
    content: string;
    model: string;
    is_chunk: boolean;
    type: string;
    metadata: Record<string, any>
    created_at: string

}
export type GetPineconeIndexRecordsResponse = PineconeIndexRecord[]

export type GetPineconeIndexRecordRequest = {
    index_name: string;
    record_id: string;
}

export type GetPineconeIndexRecordResponse = {
    id: string,
    metadata: Record<string, any>
    vector: number[]
}

export type DeletePineconeIndexRecordRequest = {
    index_name: string;
    record_id: string;
}


type ChunkConfigType = {
    overlap: string;
    chunk_size: string;
}


export type PineconeEmbedRequestText = {
    "index_name": string;
    "lexical_index_name"?: string;
    "embed_model": string;
    "input_mode": string;
    "data": string;
    "chunk_config"?: ChunkConfigType;
}

export type PineconeEmbedRequestForm = {
    "index_name": string;
    "embed_model": string;
    "lexical_index_name"?: string;
    "input_mode": string;
    "files": Array<File>
    "chunk_config"?: string;
}

export type PineconeEmbedResponse = {
    status: string;
    message: string;
}
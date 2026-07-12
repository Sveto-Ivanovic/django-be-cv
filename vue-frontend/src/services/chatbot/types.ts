export type SupabaseMetadata = {
    namespace: string;
    top_k: number;
    mode: string;
    table_name: string;
    model: string;
    semantic_search_mode: string;
}

export type PineconeMetadata = {
    index_name: string;
    top_k: number;
    mode: string;
    index_name_lexical?: string;
    model: string;
}


export type ChatbotRequest = {
    question: string;
    llm_model: string;
    conv_id?: string;
    supabase_metadata?: SupabaseMetadata;
    pinecone_metadata?: PineconeMetadata;
}

export type ChatbotResponse = {
response: string;
conv_id: string;
}


export type GetConvHistoryResponse ={
    id: string;
    name: string;   
}[]

export type GetMessagesRequest = {
    conv_id: string;
}

export type GetMessagesResponse = {
    question: string;
    answer: string;
    created_at: string;
}[]
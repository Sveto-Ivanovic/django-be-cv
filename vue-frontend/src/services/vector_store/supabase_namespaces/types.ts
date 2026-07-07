export type SupabaseNamespace = {
    namespace: string;
    model: string;
    row_count: number;
    additional_info: string | null | undefined;
    updated_at: string;
    created_at: string;
    supabase_table_name: string;
}

export type GetSupabaseNamespacesResponse= SupabaseNamespace[]

export type DeleteSupabaseRecordsRequest = {
    table_name: string;
    ids: string[];
    namespace: string;
}

export type DeleteSupabaseRecordsResponse = {
    message: string;
    delete_count: string;
    details: Record<string, number>;
}


export type GetSupabaseNamespaceRecordsRequest = {
    table_name: string;
    namespace: string;
}

export type SupabaseNamespaceRecord = {
    id: string,
    namespace: string;
    source: string;
    chunk_number: number;
    content: string;
    model: string;
    is_chunk: boolean;
    type: string;
    metadata: Record<string, any>
    created_at: string

}

export type GetSupabaseNamespacesRecordsResponses = {
    records: SupabaseNamespaceRecord[];
    count: number;
    table_name: string;
    namespace: string;
}

export type DeleteSupabaseNamespaceRequest = {
    table_name: string;
    namespace: string;
}
export type DeleteSupabaseNamespaceResponse = {
    table_name: string;
    namespace: string;
    message: string;
    delete_count: string;
}
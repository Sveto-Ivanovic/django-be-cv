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
    ids_to_delete: string[];
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

export type GetSupabaseNamespacesRecordsResponses = {
    records: any[];
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
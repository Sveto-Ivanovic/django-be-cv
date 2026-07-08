import { get } from 'http'
import http from '../../axios_service/api'
import { APIResponse } from '../../axios_service/axiosTypes'
import {
    GetSupabaseNamespacesResponse, GetSupabaseNamespaceRecordsRequest, GetSupabaseNamespacesRecordsResponses, DeleteSupabaseNamespaceRequest,
    DeleteSupabaseNamespaceResponse, DeleteSupabaseRecordsRequest, DeleteSupabaseRecordsResponse, SupabaseEmbedRequestForm, SupabaseEmbedRequestText, SupabaseEmbedResponse
} from './types'
import { useMutation, UseMutationReturnType, useQuery, useQueryClient  } from '@tanstack/vue-query'
import { useUserStore } from '../../../stores/user_store'
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { AxiosResponse } from 'axios'

function buildEmbedFormData(req: SupabaseEmbedRequestForm): FormData {
    const fd = new FormData()
    fd.append('namespace', req.namespace)
    fd.append('embed_model', req.embed_model)
    fd.append('input_mode', req.input_mode)

    if (req.files)
        req.files.forEach(file => fd.append('files', file))

    if (req.chunk_config) {
        fd.append('chunk_config', JSON.stringify(req.chunk_config))
    }

    return fd
}



const api = {

    getUserSupabaseNamespace: () =>
        http.get<APIResponse<GetSupabaseNamespacesResponse | null | string>>('embed/get_supabase_tables/'),
    getUserNamespaceData: (data: GetSupabaseNamespaceRecordsRequest) => http.get<APIResponse<GetSupabaseNamespacesRecordsResponses | null | string>>(`embed/list_supabase_table_records/?namespace=${data.namespace}&table_name=${data.table_name}`),
    deleteNamespace: (data: DeleteSupabaseNamespaceRequest) => http.post<APIResponse<DeleteSupabaseNamespaceResponse | null | undefined | string>>('embed/delete_supabase_namespace/', data),
    deleteRecord: (data: DeleteSupabaseRecordsRequest) => http.post<APIResponse<DeleteSupabaseRecordsResponse | null | undefined | string>>('embed/delete_supabase_records/', data),
    embedSupabase: (data: SupabaseEmbedRequestText) => http.post<APIResponse<SupabaseEmbedResponse | string | undefined>>('embed/embed_items_into_supabase/', data),
    embedSupabaseForm: (data: SupabaseEmbedRequestForm) => http.post<APIResponse<SupabaseEmbedResponse | string | undefined>>('embed/embed_items_into_supabase/', buildEmbedFormData(data), {headers:{
        'Content-Type': "multipart/form-data"
    }})

    

}


function fetchSupabaseNamespaces() {
    const userStore = useUserStore();
    const route = useRoute()

    const query = useQuery({
        queryKey: ['supabase_namespaces'],
        queryFn: () => api.getUserSupabaseNamespace(),
        enabled: computed(() => {

            if (route.name) {
                return userStore.isAuthenticated && route.name as string == "SupabaseNameSpaces"
            }
            else {
                return false
            }
        }),
    });
    return { ...query };
}


function fetchSupabaseNamespaceRecords(req: GetSupabaseNamespaceRecordsRequest) {
    const userStore = useUserStore();
    const route = useRoute()

    const query = useQuery({
        queryKey: ['supabase_namespace_records'],
        queryFn: () => api.getUserNamespaceData(req),
        enabled: computed(() => {

            if (route.name) {
                return userStore.isAuthenticated && route.name as string == "SupabaseNamespaceRecords"
            }
            else {
                return false
            }
        }),
    });
    return { ...query };
}


function deleteNamespace() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationKey: ['delete_namespace_supabase'],
        mutationFn: (req: DeleteSupabaseNamespaceRequest) => api.deleteNamespace(req),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['supabase_namespaces', 'supabase_namespace_records'] })
        }
    })
}


function deleteRecord() {
    return useMutation({
        mutationKey: ['delete_record_supabase'],
        mutationFn: (req: DeleteSupabaseRecordsRequest) => api.deleteRecord(req),

    })
}

function embedSupabaseRecords(isMultiform: true): UseMutationReturnType<any, Error, SupabaseEmbedRequestForm, unknown>
function embedSupabaseRecords(isMultiform: false): UseMutationReturnType<any, Error, SupabaseEmbedRequestText, unknown>
function embedSupabaseRecords(isMultiform: boolean) {
    const queryClient = useQueryClient()

    if(isMultiform){
        return useMutation({
            mutationKey: ['embed_supabase_records_multiform'],
            mutationFn: (req: SupabaseEmbedRequestForm) => api.embedSupabaseForm(req),
            onSuccess: (data) => {
                queryClient.invalidateQueries({ queryKey: ['supabase_namespaces', 'supabase_namespace_records'] })
            }
        })
    }

    return useMutation({
        mutationKey: ['embed_supabase_records_text'],
        mutationFn: (req: SupabaseEmbedRequestText) => api.embedSupabase(req),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['supabase_namespaces', 'supabase_namespace_records'] })
        }
    })
}


export default {
    fetchSupabaseNamespaces,
    fetchSupabaseNamespaceRecords,
    deleteNamespace,
    deleteRecord,
    embedSupabaseRecords,
    api
}


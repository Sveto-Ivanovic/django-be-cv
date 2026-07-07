import { get } from 'http'
import http from '../../axios_service/api'
import { APIResponse } from '../../axios_service/axiosTypes'
import {
    GetSupabaseNamespacesResponse, GetSupabaseNamespaceRecordsRequest, GetSupabaseNamespacesRecordsResponses, DeleteSupabaseNamespaceRequest, 
    DeleteSupabaseNamespaceResponse, DeleteSupabaseRecordsRequest, DeleteSupabaseRecordsResponse
} from './types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useUserStore } from '../../../stores/user_store'
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'


const api = {

    getUserSupabaseNamespace: () =>
        http.get<APIResponse<GetSupabaseNamespacesResponse | null | string>>('embed/get_supabase_tables/'),
    getUserNamespaceData: (data: GetSupabaseNamespaceRecordsRequest) => http.get<APIResponse<GetSupabaseNamespacesRecordsResponses | null | string>>(`embed/list_supabase_table_records/?namespace=${data.namespace}&table_name=${data.table_name}`),
    deleteNamespace: (data: DeleteSupabaseNamespaceRequest) => http.post<APIResponse<DeleteSupabaseNamespaceResponse | null | undefined | string>>('embed/delete_supabase_namespace/', data),
    deleteRecord: (data: DeleteSupabaseRecordsRequest) => http.post<APIResponse<DeleteSupabaseRecordsResponse | null | undefined | string>>('embed/delete_supabase_records/', data)


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
        mutationKey: ['delete_namespace'],
        mutationFn: (req: DeleteSupabaseNamespaceRequest) => api.deleteNamespace(req),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['supabase_namespaces', 'supabase_namespaces'] })
        }
    })
}


function deleteRecord() {
    return useMutation({
        mutationKey: ['delete_record'],
        mutationFn: (req: DeleteSupabaseRecordsRequest) => api.deleteRecord(req),
 
    })
}



export default {
    fetchSupabaseNamespaces,
    fetchSupabaseNamespaceRecords,
    deleteNamespace,
    deleteRecord,
    api
}
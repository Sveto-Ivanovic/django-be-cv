import { get } from 'http'
import http from '../../axios_service/api'
import { APIResponse } from '../../axios_service/axiosTypes'
import {
    GetSupabaseNamespacesResponse
} from './types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useUserStore } from '../../../stores/user_store'
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'


const api = {

    getUserSupabaseNamespace: () =>
        http.get<APIResponse<GetSupabaseNamespacesResponse | null | string>>('embed/get_supabase_tables/'),


}


function fetchSupabaseNamespaces() {
    const userStore = useUserStore();
    const route = useRoute()

    const query = useQuery({
        queryKey: ['pinecone_indexes'],
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


export default {
    fetchSupabaseNamespaces,
    api
}
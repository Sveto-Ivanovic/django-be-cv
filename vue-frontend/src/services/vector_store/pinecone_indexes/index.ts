import { get } from 'http'
import http from '../../axios_service/api'
import { APIResponse } from '../../axios_service/axiosTypes'
import {
    GetPineconeIndexesResponse
} from './types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useUserStore } from '../../../stores/user_store'
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'


const api = {

    getUserPineconeIndexes: () =>
        http.get<APIResponse<GetPineconeIndexesResponse | null | string>>('embed/get_pinecone_indexes/'),


}


function fetchPineconeIndexes() {
    const userStore = useUserStore();
    const route = useRoute()

    const query = useQuery({
        queryKey: ['pinecone_indexes'],
        queryFn: () => api.getUserPineconeIndexes(),
        enabled: computed(() => {

            if (route.name) {
                return userStore.isAuthenticated && route.name as string == "PineconeIndexes"
            }
            else {
                return false
            }
        }),
    });
    return { ...query };
}


export default {
    fetchPineconeIndexes,
    api
}
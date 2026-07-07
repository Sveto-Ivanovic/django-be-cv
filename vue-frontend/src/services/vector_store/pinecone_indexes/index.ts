import { get } from 'http'
import http from '../../axios_service/api'
import { APIResponse } from '../../axios_service/axiosTypes'
import {
    GetPineconeIndexesResponse, GetPineconeIndexRecordsRequest, GetPineconeIndexRecordsResponse, DeletePineconeIndexRecordRequest,
    DeletePineconeIndexRequest, DeletePineconeIndexTextSearchRequest, DeletePineconeIndexTextSearchResponse, CreatePineconeIndexRequest,
    CreatePineconeIndexResponse, CreatePineconeIndexTextSearchRequest, CreatePineconeIndexTextSearchResponse
} from './types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useUserStore } from '../../../stores/user_store'
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'


const api = {

    getUserPineconeIndexes: () =>
        http.get<APIResponse<GetPineconeIndexesResponse | null | string>>('embed/get_pinecone_indexes/'),
    getUserPineconeIndexRecords: (data: GetPineconeIndexRecordsRequest) => http.get<APIResponse<GetPineconeIndexRecordsResponse | null | string>>(`embed/fetch_pinecone_index_data/?index_name=${data.index_name}`),
    deletePineconeIndex: (data: DeletePineconeIndexRequest) => http.post<APIResponse<string | null | undefined>>('embed/delete_pinecone_index/', data),
    deletePineconeIndexRecord: (data: DeletePineconeIndexRecordRequest) => http.post<APIResponse<string | null | undefined>>('embed/delete_pinecone_index_record/', data),
    deletePineconeIndexTextsearch: (data: DeletePineconeIndexTextSearchRequest) => http.post<APIResponse<DeletePineconeIndexTextSearchResponse | string | null | undefined>>('embed/delete_textsearch_index/', data),
    createPineconeIndex: (data: CreatePineconeIndexRequest) => http.post<APIResponse<CreatePineconeIndexResponse | string | undefined | null>>('embed/create_pinecone_index/', data),
    createPineconeIndexTextsearch: (data: CreatePineconeIndexTextSearchRequest) => http.post<APIResponse<CreatePineconeIndexTextSearchResponse | string | undefined | null>>('embed/create_textsearch_index/', data),
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


function fetchPineconeIndexRecords(req: GetPineconeIndexRecordsRequest) {
    const userStore = useUserStore();
    const route = useRoute()

    const query = useQuery({
        queryKey: ['pinecone_index_records'],
        queryFn: () => api.getUserPineconeIndexRecords(req),
        enabled: computed(() => {

            if (route.name) {
                return userStore.isAuthenticated && route.name as string == "PineconeIndexRecords"
            }
            else {
                return false
            }
        }),
    });
    return { ...query };
}


function deletePineconeIndex() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationKey: ['delete_pinecone_index'],
        mutationFn: (req: DeletePineconeIndexRequest) => api.deletePineconeIndex(req),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['pinecone_indexes', 'pinecone_index_records'] })
        }
    })
}

function deletePineconeIndexRecord() {
    return useMutation({
        mutationKey: ['delete_pinecone_index_record'],
        mutationFn: (req: DeletePineconeIndexRecordRequest) => api.deletePineconeIndexRecord(req)
    })
}


function deletePineconeIndexTextsearch() {

    return useMutation({
        mutationKey: ['delete_pinecone_index_textsearch'],
        mutationFn: (req: DeletePineconeIndexTextSearchRequest) => api.deletePineconeIndexTextsearch(req)
    })
}


function createPineconeIndex() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationKey: ['create_pinecone_index'],
        mutationFn: (req: CreatePineconeIndexRequest) => api.createPineconeIndex(req),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['pinecone_indexes'] })
        }
    })
}

function createPineconeIndexTextsearch() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationKey: ['create_pinecone_index'],
        mutationFn: (req: CreatePineconeIndexTextSearchRequest) => api.createPineconeIndexTextsearch(req),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['pinecone_indexes'] })
        }
    })
}


export default {
    fetchPineconeIndexes,
    fetchPineconeIndexRecords,
    deletePineconeIndex,
    deletePineconeIndexRecord,
    deletePineconeIndexTextsearch,
    createPineconeIndex,
    createPineconeIndexTextsearch,
    api
}
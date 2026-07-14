import http from '../../axios_service/api'
import type { APIResponse } from '../../axios_service/axiosTypes'
import type {
    GetPineconeIndexesResponse, GetPineconeIndexRecordsRequest, GetPineconeIndexRecordsResponse, DeletePineconeIndexRecordRequest,
    DeletePineconeIndexRequest, DeletePineconeIndexTextSearchRequest, DeletePineconeIndexTextSearchResponse, CreatePineconeIndexRequest,
    CreatePineconeIndexResponse, CreatePineconeIndexTextSearchRequest, CreatePineconeIndexTextSearchResponse,
    PineconeEmbedRequestForm, PineconeEmbedRequestText, PineconeEmbedResponse
} from './types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import type { UseMutationReturnType } from '@tanstack/vue-query'

import { useUserStore } from '../../../stores/user_store'
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

function buildEmbedFormData(req: PineconeEmbedRequestForm): FormData {
    const fd = new FormData()
    fd.append('index_name', req.index_name)
    fd.append('embed_model', req.embed_model)
    fd.append('input_mode', req.input_mode)
    
    if (req.lexical_index_name) {
        fd.append('lexical_index_name', req.lexical_index_name)
    }

    if (req.files)
        req.files.forEach(file => fd.append('files', file))

    if (req.chunk_config) {
        fd.append('chunk_config', JSON.stringify(req.chunk_config))
    }

    return fd
}


const api = {

    getUserPineconeIndexes: () =>
        http.get<APIResponse<GetPineconeIndexesResponse | null | string>>('embed/get_pinecone_indexes/'),
    getUserPineconeIndexRecords: (data: GetPineconeIndexRecordsRequest) => http.get<APIResponse<GetPineconeIndexRecordsResponse | null | string>>(`embed/fetch_pinecone_index_data/?index_name=${data.index_name}`),
    deletePineconeIndex: (data: DeletePineconeIndexRequest) => http.post<APIResponse<string | null | undefined>>('embed/delete_pinecone_index/', data),
    deletePineconeIndexRecord: (data: DeletePineconeIndexRecordRequest) => http.post<APIResponse<string | null | undefined>>('embed/delete_pinecone_index_record/', data),
    deletePineconeIndexTextsearch: (data: DeletePineconeIndexTextSearchRequest) => http.post<APIResponse<DeletePineconeIndexTextSearchResponse | string | null | undefined>>('embed/delete_textsearch_index/', data),
    createPineconeIndex: (data: CreatePineconeIndexRequest) => http.post<APIResponse<CreatePineconeIndexResponse | string | undefined | null>>('embed/create_pinecone_index/', data),
    createPineconeIndexTextsearch: (data: CreatePineconeIndexTextSearchRequest) => http.post<APIResponse<CreatePineconeIndexTextSearchResponse | string | undefined | null>>('embed/create_textsearch_index/', data),
     embedPinecone: (data: PineconeEmbedRequestText) => http.post<APIResponse<PineconeEmbedResponse | string | undefined>>('embed/embed_items_into_pinecone/', data),
    embedPineconeForm: (data: PineconeEmbedRequestForm) => http.post<APIResponse<PineconeEmbedResponse | string | undefined>>('embed/embed_items_into_pinecone/', buildEmbedFormData(data), {headers:{
        'Content-Type': "multipart/form-data"
    }})

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



function embedPineconeRecords(isMultiform: true): UseMutationReturnType<any, Error, PineconeEmbedRequestForm, unknown>
function embedPineconeRecords(isMultiform: false): UseMutationReturnType<any, Error, PineconeEmbedRequestText, unknown>
function embedPineconeRecords(isMultiform: boolean) {
    const queryClient = useQueryClient()

    if (isMultiform) {
        return useMutation({
            mutationKey: ['embed_pinecone_records_multiform'],
            mutationFn: (req: PineconeEmbedRequestForm) => api.embedPineconeForm(req),
            onSuccess: (data) => {
                queryClient.invalidateQueries({ queryKey: ['pinecone_index_records', 'pinecone_indexes'] })
            }
        })
    }

    return useMutation({
        mutationKey: ['embed_records_records_text'],
        mutationFn: (req: PineconeEmbedRequestText) => api.embedPinecone(req),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['pinecone_index_records', 'pinecone_indexes'] })
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
    embedPineconeRecords,
    api
}
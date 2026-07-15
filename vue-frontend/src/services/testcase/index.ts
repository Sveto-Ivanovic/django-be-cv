import http from '../axios_service/api'
import type { APIResponse } from '../axios_service/axiosTypes'
import type { TestCaseRequest, TestCaseResponse, GetAggregateResponse, DeleteTestCaseRequest, ValidateJsonRequest, ValidateTextRequest, ValidateTextResponse } from './types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useUserStore } from '../../stores/user_store'
import { computed,  } from 'vue'
import { useRoute,  } from 'vue-router'

function buildForm(req: ValidateJsonRequest): FormData {
    const fd = new FormData()
    fd.append('testcase_name', req.testcase_name)
    fd.append('llm_model', req.llm_model)
    fd.append('eval_model', req.eval_model)

    if (req.to_evaluate) {
        fd.append('to_evaluate', req.to_evaluate)
    }

    if (req.supabase_metadata) {
        fd.append('supabase_metadata', JSON.stringify(req.supabase_metadata))
    }
    if (req.pinecone_metadata) {
        fd.append('pinecone_metadata', JSON.stringify(req.pinecone_metadata))
    }

    if (req.nearest_neighbor_settings) {
        fd.append('nearest_neighbor_settings', JSON.stringify(req.nearest_neighbor_settings))
    }

    return fd
}



const api = {
    getAggregateEvals: () => http.get<APIResponse<GetAggregateResponse | null | string>>('evaluate/get_eval_aggregates/'),
    getTestCaseEvals: (data: TestCaseRequest) => http.get<APIResponse<TestCaseResponse | null | string>>(`evaluate/get_eval_testcases/?aggregate_id=${data.aggregate_id}`),
    deleteAggregate: (data: DeleteTestCaseRequest) => http.post<APIResponse<null | undefined | string>>('evaluate/delete_eval_aggregate/', data),
    validateTextRequest: (data: ValidateTextRequest) => http.post<APIResponse<ValidateTextResponse | string | undefined>>('evaluate/call_eval_text/', data),
    validateJsonRequest: (data: ValidateJsonRequest) => http.post<APIResponse<ValidateTextResponse | string | undefined>>('evaluate/call_eval_json/', buildForm(data), {
        headers: {
            'Content-Type': "multipart/form-data"
        }
    })
}


function getAggregateResults() {
    const userStore = useUserStore();
    const route = useRoute()

    const query = useQuery({
        queryKey: ['fetch_aggregates'],
        queryFn: () => api.getAggregateEvals(),
        enabled: computed(() => {

            if (route.name) {
                return userStore.isAuthenticated && route.name as string == "TestCaseResults"
            }
            else {
                return false
            }
        }),
    });
    return { ...query };
}

function getTestCaseEvals(req: TestCaseRequest) {
    const userStore = useUserStore();
    const route = useRoute()

    const query = useQuery({
        queryKey: ['fetch_testcases'],
        queryFn: () => api.getTestCaseEvals(req),
        enabled: computed(() => {

            if (route.name) {
                return userStore.isAuthenticated && route.name as string == "TestCaseResultStatistics"
            }
            else {
                return false
            }
        }),
    });
    return { ...query };
}



function deleteAggregate() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationKey: ['delete_aggregate'],
        mutationFn: (req: DeleteTestCaseRequest) => api.deleteAggregate(req),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['fetch_aggregates', 'fetch_testcases'] })
        }
    })
}

function validateText() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationKey: ['validate_testcase_text'],
        mutationFn: (req: ValidateTextRequest) => api.validateTextRequest(req),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['fetch_aggregates'] })
        }
    })


}

function validateJson() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationKey: ['validate_testcase_text'],
        mutationFn: (req: ValidateJsonRequest) => api.validateJsonRequest(req),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['fetch_aggregates'] })
        }
    })
}

export default {
    getAggregateResults,
    getTestCaseEvals,
    deleteAggregate,
    validateText,
    validateJson,
    api
}


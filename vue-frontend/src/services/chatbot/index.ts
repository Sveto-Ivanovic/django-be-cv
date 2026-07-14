import http from '../axios_service/api'
import { APIResponse } from '../axios_service/axiosTypes'
import { ChatbotRequest, ChatbotResponse, GetConvHistoryResponse, GetMessagesResponse, GetMessagesRequest } from './types'
import { useMutation, UseMutationReturnType, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useUserStore } from '../../stores/user_store'
import { computed, MaybeRefOrGetter, toValue, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { AxiosResponse } from 'axios'


const api = {
    getChatHistory: () => http.get<APIResponse<GetConvHistoryResponse | null | string>>('chatbot/get_history/'),
    getMessages: (data: GetMessagesRequest) => http.get<APIResponse<GetMessagesResponse | null | string>>(`chatbot/get_conv_history/?conv_id=${data.conv_id}`),
    callChatbot: (data: ChatbotRequest) => http.post<APIResponse<ChatbotResponse | undefined | string>>('chatbot/call_chatbot/', data),

}


function getChatbotHistory() {
    const userStore = useUserStore();
    const route = useRoute()

    const query = useQuery({
        queryKey: ['fetch_history'],
        queryFn: () => api.getChatHistory(),
        enabled: computed(() => {

            if (route.name) {
                return userStore.isAuthenticated && route.name as string == "ChatbotPage"
            }
            else {
                return false
            }
        }),
    });
    return { ...query };
}

function getChatMessages(req: MaybeRefOrGetter<GetMessagesRequest>) {
    const userStore = useUserStore();
    const route = useRoute()
    const queryClient = useQueryClient()
    const queryKey = computed(() => ['fetch_chat_messages', toValue(req).conv_id])



    const query = useQuery({
        queryKey,
        queryFn: () => api.getMessages(toValue(req)),
        enabled: computed(() => {
            const convId = toValue(req).conv_id
            if (route.name) {
                return userStore.isAuthenticated && route.name as string == "ChatbotPage" && !!convId
            }
            else {
                return false
            }
        }),
    });

    function seedMessages(convId: string, response: AxiosResponse<APIResponse<GetMessagesResponse | null | string>>) {
        queryClient.setQueryData(['fetch_chat_messages', convId], response)
    }
    return { ...query, seedMessages };
}



function callChatbot() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationKey: ['call_chatbot'],
        mutationFn: (req: ChatbotRequest) => api.callChatbot(req),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['fetch_history'] })
        }
    })
}

export default {
    getChatbotHistory,
    getChatMessages,
    callChatbot,
    api
}


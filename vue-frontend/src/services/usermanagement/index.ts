import http from '../axios_service/api'
import type { APIResponse } from '../axios_service/axiosTypes'
import type {
    RegisterRequest, SuccessFullRegistrationResponse,
    LogInRequest, LogInResponse, UserInfo,
    RefreshTokenRequest, RefreshTokenResponse, LogOutRequest,
    UpdateUserKeyRequest, DeleteUserKeyRequest
} from './types'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { useUserStore } from '../../stores/user_store'
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'


const api = {
    registerUser: (req: RegisterRequest) =>
        http.post<APIResponse<SuccessFullRegistrationResponse | null | string>>('user/register_user/', req),
    loginUser: (req: LogInRequest) =>
        http.post<APIResponse<LogInResponse | null | string>>('user/login_user/', req, {withCredentials: true}),
    getUserInfo: () =>
        http.get<APIResponse<UserInfo | null | string>>('user/get_user_info/'),
    logoutUser: (req: LogOutRequest) =>
        http.post<APIResponse<string | null>>('user/logout_user/', req, {withCredentials: true}),
    updateUserKey: (req: UpdateUserKeyRequest) =>
        http.put<APIResponse<string | null>>('user/update_user_keys/', req),
    deleteUserKey: (req: DeleteUserKeyRequest) =>
        http.put<APIResponse<string | null>>('user/remove_key/', req),
    refreshUserToken: (req: RefreshTokenRequest) => http.post<APIResponse<RefreshTokenResponse | string | null>>('user/refresh_token/', req, {withCredentials: true})

}



function loginUser() {
    const userStore = useUserStore();
    return useMutation({
        mutationKey: ['login'],
        mutationFn: (req: LogInRequest) => api.loginUser(req),
        onSuccess: (data) => {
            userStore.logOutUser()
            if (typeof data.data.response === 'object' && data.data.response !== null && 'access_token' in data.data.response) {
                userStore.initUser(data.data.response);
            }
        }
    })
}

function registerUser() {
    return useMutation({
        mutationKey: ['register'],
        mutationFn: (req: RegisterRequest) => api.registerUser(req),
    })
}


function fetchUserInfo() {
    const userStore = useUserStore();
    userStore.removeUserInfo()
    const route = useRoute()
    const dontRefetchOn = ['Home', 'Contact', 'About', 'Register', 'Login', 'Missing', 'ConfirmEmail', 'NotFound']

    const query = useQuery({
        queryKey: ['user_info', 'auth'],
        queryFn: () => api.getUserInfo(),
        enabled: computed(() => {

            if (route.name) {
                return userStore.isAuthenticated && !dontRefetchOn.includes(route.name as string)
            }
            else {
                return false
            }
        }),
    });

    watch(query.data, (data) => {
        const response = data?.data.response
        if (typeof response === 'object' && response !== null) {
            userStore.setUserInfo(response as UserInfo);

        }
    });

    return { ...query };
}


function deleteKey() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationKey: ['delete_key'],
        mutationFn: (req: DeleteUserKeyRequest) => api.deleteUserKey(req),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['user_info'] })
        }
    })
}

function updateKey() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationKey: ['update_key'],
        mutationFn: (req: UpdateUserKeyRequest) => api.updateUserKey(req),
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['user_info'] })
        }
    })
}


function logOutUser() {
    const userStore = useUserStore()
    return useMutation({
        mutationKey: ['logout', 'auth'],
        mutationFn: () => api.logoutUser({
            access_token: userStore.accessToken as string
        }),
        onSuccess: (data) => {
            userStore.logOutUser()
        },
        
    })
}


export default {
    loginUser,
    registerUser,
    fetchUserInfo,
    deleteKey,
    updateKey,
    logOutUser,
    api
}
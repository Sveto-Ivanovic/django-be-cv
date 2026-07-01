import { get } from 'http'
import http from '../axios_service/api'
import { APIResponse } from '../axios_service/axiosTypes'
import {
    RegisterRequest, SuccessFullRegistrationResponse,
    LogInRequest, LogInResponse, UserInfo,
    RefreshTokenRequest, RefreshTokenResponse, LogOutRequest,
    UpdateUserKeyRequest, DeleteUserKeyRequest
} from './types'
import { useMutation, useQuery } from '@tanstack/vue-query'
import { useUserStore } from '../../stores/user_store'


const api = {
    registerUser: (req: RegisterRequest) =>
        http.post<APIResponse<SuccessFullRegistrationResponse | null | string>>('user/register_user/', req),
    loginUser: (req: LogInRequest) =>
        http.post<APIResponse<LogInResponse | null | string>>('user/login_user/', req),
    getUserInfo: () =>
        http.get<APIResponse<UserInfo | null | string>>('user/get_user_info/'),
    logoutUser: (req: LogOutRequest) =>
        http.post<APIResponse<string | null>>('user/logout_user/', req),
    updateUserKey: (req: UpdateUserKeyRequest) =>
        http.put<APIResponse<string | null>>('user/update_user_keys/', req),
    deleteUserKey: (req: DeleteUserKeyRequest) =>
        http.put<APIResponse<string | null>>('user/remove_key/', req),

}



function loginUser() {
    const userStore = useUserStore();
    return useMutation({
        mutationKey: ['login'],
        mutationFn: (req: LogInRequest) => api.loginUser(req),
         onSuccess: (data)=>{
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



/*
function useGetContacts() {
  return useQuery({
    queryKey: ['contact', 'list'],
    queryFn: () => api.getContacts(),
  })
}
*/
export default {
    loginUser,
    registerUser,
    api
}
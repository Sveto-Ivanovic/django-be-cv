import axios, { AxiosError } from 'axios';
import type { AxiosRequestConfig } from 'axios'
import { useUserStore } from '../../stores/user_store';
import type { APIResponse } from './axiosTypes';
import {getRouterInstance} from '../../router/router_instance';


const instance = axios.create({
  baseURL: import.meta.env.VITE_BE_HOST,
});

const refreshClient = axios.create({
  baseURL: import.meta.env.VITE_BE_HOST,
  withCredentials: true,
});


interface RetryableConfigCustom extends AxiosRequestConfig {
  hasRetried?: boolean
}

instance.interceptors.request.use(
  function (config) {
    const userStore = useUserStore();
    const accessToken = userStore.accessToken;

    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    return config;

  },
)

function forceLogout() {
  const router = getRouterInstance();
  const userStore = useUserStore();

  if (userStore.isAuthenticated) {
    userStore.logOutUser();
  }

  if (!router) {
    window.location.replace('/login');
    return;
  }

  if (router.currentRoute.value.name !== 'Login') {
    router.push({ name: 'Login' }).catch(() => {});
  }
}

let isRefreshing = false
let refreshSubs: Array<(token: string | null) => void> = []
function subscribeTokenRefresh(cb: (token: string | null) => void) {
  refreshSubs.push(cb)
}
function refreshSubscribers(token: string | null) {
  refreshSubs.forEach((cb) => cb(token))
  refreshSubs = []
}


instance.interceptors.response.use(
  function (response) {
    return response;
  },
  async function (error) {
    const axiosError = error as AxiosError<APIResponse<string>>
    const originalRequest = axiosError.config as RetryableConfigCustom | undefined;


    if (axiosError.response?.status !== 401 || !originalRequest) {
      return Promise.reject(error);
    }

    if (originalRequest.hasRetried) {
      forceLogout();
      return Promise.reject(error);
    }

    originalRequest.hasRetried = true

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        subscribeTokenRefresh((token) => {

          if (token === null) {
            reject(error)
            return
          }

          originalRequest.headers = {
            ...originalRequest.headers,
            Authorization: `Bearer ${token}`
          }
          resolve(instance(originalRequest));
        })
      })
    }

    isRefreshing = true

    try {
      const userStore = useUserStore();
      const accessToken = userStore.accessToken

      const response = await refreshClient.post<APIResponse<{ access_token: string; username: string } | string>>('user/refresh_token/', { access_token: accessToken ?? '' })

      if (typeof response.data.response === 'string') {
        refreshSubscribers(null);
        forceLogout();
        return Promise.reject(error);
      }
      const newUser = response.data.response
      userStore.initUser(newUser)
      refreshSubscribers(newUser.access_token)

      originalRequest.headers = {
        ...originalRequest.headers,
        Authorization: `Bearer ${newUser.access_token}`
      }
      return instance(originalRequest)
    }
    catch (e) {
      refreshSubscribers(null);
      forceLogout();
      return Promise.reject(error);
    } finally {
      isRefreshing = false;
    }


  }
);

export default instance
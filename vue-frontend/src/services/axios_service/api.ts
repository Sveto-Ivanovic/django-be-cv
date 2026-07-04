import axios, { AxiosError } from 'axios';
import { useUserStore } from '../../stores/user_store'; 
import { APIResponse } from './axiosTypes';
import { useRouter } from 'vue-router';
import router from '../../router';


const instance = axios.create({
  baseURL: import.meta.env.VITE_BE_HOST,
});

instance.interceptors.request.use(
  function (config){
    const userStore = useUserStore();
    const accessToken = userStore.accessToken;

    if (accessToken){
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    return config;

  },
)


instance.interceptors.response.use(
  function (response) {
    return response;
  },
  function (error) {
    const axiosError = error as AxiosError<APIResponse<string>>

    if (axiosError.response?.status === 401) {
      const userStore = useUserStore();
      userStore.logOutUser()
      /* latter here we will implement the refresh token logic */
          router.push({name: 'Login'})
    }


    return Promise.reject(error);
  }
);

export default instance
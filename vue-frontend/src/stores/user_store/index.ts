import { defineStore } from "pinia";
import { computed, ref } from 'vue';
import type { LogInResponse } from "../../services/usermanagement/types";
import type { UserInfo } from '../../services/usermanagement/types'

export const useUserStore = defineStore("userStore", () => {
  const user = ref<LogInResponse>();

  const isAuthenticated = computed(() => !!user.value?.access_token);
  const accessToken = computed(() => user.value?.access_token);
  const email = ref("unknow@gmail.com")
  const userInfo = ref<UserInfo | undefined>(undefined)
  const hasUserInfo = ref(false)
  const hasEmbedKey = ref(false)
  const hasLLmKey = ref(false)
  const hasPineconeKey = ref(false)

  function initUser(data: LogInResponse) {
    user.value = data;
  }

  function removeUser() {
    user.value = undefined;
  }

  function setEmail(data: string) {
    email.value = data
  }

  function removeEmail() {
    email.value = "unknow@gmail.com"
  }

  function setUserInfo(data: UserInfo) {
    userInfo.value = data
    hasUserInfo.value = true
    if (!!userInfo.value?.api_keys?.has_cohere_api_key ||
      !!userInfo.value?.api_keys?.has_gemini_api_key ||
      !!userInfo.value?.api_keys?.has_jina_api_key) {
      hasEmbedKey.value = true
    }
    else {
      hasEmbedKey.value = false
    }
    if (!!userInfo.value?.api_keys?.has_groq_api_key ||
      !!userInfo.value?.api_keys?.has_gemini_api_key ||
      !!userInfo.value?.api_keys?.has_mistral_api_key) {
      hasLLmKey.value = true
    }
    else {
      hasLLmKey.value = false
    }
    if(!!userInfo.value?.api_keys?.has_pinecone_api_key){
      hasPineconeKey.value=true
    }else{
      hasPineconeKey.value=false
    }

  }

  function removeUserInfo() {
    userInfo.value = undefined
    hasUserInfo.value = false
    hasLLmKey.value = false
    hasLLmKey.value = false
    hasPineconeKey.value=false
  }

  function logOutUser() {
    removeEmail()
    removeUser()
    removeUserInfo()
  }


  return {
    user,
    email,
    isAuthenticated,
    accessToken,
    hasPineconeKey,
    userInfo,
    hasEmbedKey,
    hasLLmKey,
    hasUserInfo,
    initUser,
    removeUser,
    setEmail,
    removeEmail,
    setUserInfo,
    removeUserInfo,
    logOutUser
  };
}, {
  persist: true,
});
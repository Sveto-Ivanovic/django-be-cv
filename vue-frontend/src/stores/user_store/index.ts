import { defineStore } from "pinia";
import { computed, ref } from 'vue';
import { LogInResponse } from "../../services/usermanagement/types";

export const useUserStore = defineStore("userStore", () => {
  const user = ref<LogInResponse>();

  const isAuthenticated = computed(() => !!user.value?.access_token);
  const accessToken = computed(() => user.value?.access_token);

  function initUser(data: LogInResponse) {
    user.value = data;
  }

  function removeUser() {
    user.value = undefined;
  }

  return {
    user,
    isAuthenticated,
    accessToken,
    initUser,
    removeUser,
  };
}, {
  persist: true, 
});
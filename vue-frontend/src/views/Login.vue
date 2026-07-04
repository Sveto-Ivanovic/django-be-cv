<template>
  <div class="page-wrapper">
    <div class="form-wrapper-div">

      <n-card class="login-card" :bordered="true">
        
        <div class="login-header">
          <h1 class="login-title">Welcome back</h1>
          <p class="login-subtitle">Log in to continue to your account</p>
        </div>

        <n-form
          ref="formRef"
          label-placement="top"
          :model="formStructure"
          :rules="rules"
          class="form-class"
        >
          <div v-if="errorBox.showError" class="error-box">
            <p class="error-message">{{ errorBox.errorMessage }}</p>
          </div>

          <n-form-item label="Email" path="email">
            <n-input
              v-model:value="formStructure.email"
              placeholder="you@example.com"
              size="large"
              @keydown.enter="handleValidateClick"
            />
          </n-form-item>

          <n-form-item label="Password" path="password">
            <n-input
              v-model:value="formStructure.password"
              type="password"
              show-password-on="click"
              placeholder="Enter your password"
              size="large"
              @keydown.enter="handleValidateClick"
            />
          </n-form-item>

          <div class="form-options">
            <n-checkbox v-model:checked="rememberMe">
              Remember me
            </n-checkbox>
            <a class="forgot-link" href="#" @click.prevent="handleForgotPassword">
              Forgot password?
            </a>
          </div>

          <n-form-item>
            <n-button
              type="primary"
              size="large"
              color="#8a2be2"
              block
              :loading="loading"
              @click="handleValidateClick"
            >
              Log In
            </n-button>
          </n-form-item>
        </n-form>

        <div class="signup-row">
          Don't have an account?
          <a href="#" class="signup-link" @click.prevent="handleSignUp">Sign up</a>
        </div>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FormInst } from 'naive-ui'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { globalAPI} from '../services'
import { AxiosError } from 'axios'
import {APIResponse} from '../services/axios_service/axiosTypes'
import { useUserStore } from '../stores/user_store'


const userStore = useUserStore()
const {mutateAsync, isPending} = globalAPI.userManagment.loginUser()
const router = useRouter()
const formRef = ref<FormInst | null>(null)
const loading = ref(false)
const rememberMe = ref(false)
const errorBox = ref({
  showError: false,
  errorMessage: ''
})

const formStructure = ref({
  email: '',
  password: ''
})

const rules = {
  email: [
    {
      required: true,
      message: 'Please input your email',
      trigger: ['input', 'blur']
    },
    {
      type: 'email' as const,
      message: 'Please enter a valid email address',
      trigger: ['input', 'blur']
    }
  ],
  password: {
    required: true,
    message: 'Please input your password',
    trigger: ['input', 'blur']
  }
}

function handleValidateClick(e: MouseEvent | KeyboardEvent) {
  e.preventDefault()
  formRef.value?.validate( async (errors) => {
    if (!errors) {
      loading.value = true
      
      try {
        userStore.logOutUser()
        const response = await mutateAsync({
          email: formStructure.value.email,
          password: formStructure.value.password
        })
        errorBox.value.showError = false
        errorBox.value.errorMessage = ''
        loading.value = false
        router.push({
          name: "Dashboard"
        })
      } catch (error) {
        let errorAxios = error as AxiosError<APIResponse<string>>
        errorBox.value.showError = true
        errorBox.value.errorMessage = errorAxios?.response?.data.response || 'An error occurred during login. Please try again.'
        loading.value = false
      }
    }
    else {
      console.log("Validation errors:", errors)
    }
  })
}

function handleForgotPassword() {
  alert("Didn't implement this flow yet, but hey it looks good.")
}

function handleSignUp() {
  router.push({ name: 'Register' })
}
</script>

<style scoped>
.page-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;

}

.form-wrapper-div {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding-top: 64px;
}

.login-card {
  width: 420px;
  max-width: 100%;
  border-color: var(--login-border-color, rgba(0, 0, 0, 0.1));
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  border-radius: 12px;
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
}

.login-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px;
}

.login-subtitle {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.5);
  margin: 0;
}

.form-class {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 13px;
}

.forgot-link {
  color: var(--forgot-link-color, #18a058);
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
}

.signup-row {
  text-align: center;
  font-size: 13px;
  margin-top: 8px;
  color: rgba(0, 0, 0, 0.6);
}

.signup-link {
  color: var(--forgot-link-color, #18a058);
  text-decoration: none;
  font-weight: 500;
  margin-left: 4px;
}

.signup-link:hover {
  text-decoration: underline;
}

.error-box {
  background-color: #ede5e5;
  text-align: center;
  border: 1px solid #ff4d4f;
  padding: 8px;
  margin-bottom: 16px;
  border-radius: 4px;
}

@media (max-width: 600px) {
  .page-wrapper {
    padding: 12px;
    align-items: flex-start;
    padding-top: 40px;
  }

  .login-card {
    width: 100%;
    box-shadow: none;
    border: none;
    padding: 0;
  }

  .login-title {
    font-size: 20px;
  }

  .form-options {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
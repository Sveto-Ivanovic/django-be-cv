<template>

  <div class="register-page">

    <div class="card-wrapper">
      <n-card class="register-card">

        <div class="register-header">
          <h1>Get Started Now</h1>
        </div>

        <n-form class="register-form-class" ref="formRef" :model="modelRef" :rules="rules">

          <div v-if="errorBox.showError" class="error-box">
            <p class="error-message">{{ errorBox.errorMessage }}</p>
          </div>

          <n-form-item path="username" label="Username">
            <n-input size="large" v-model:value="modelRef.username" @keydown.enter.prevent />
          </n-form-item>

          <n-form-item path="name" label="Name">
            <n-input size="large" v-model:value="modelRef.name" @keydown.enter.prevent />
          </n-form-item>

          <n-form-item path="surname" label="Surname">
            <n-input size="large" v-model:value="modelRef.surname" @keydown.enter.prevent />
          </n-form-item>

          <n-form-item :span="12" label="Date of Birth" path="date_of_birth">
            <n-date-picker size="large" style="width: 100%;" v-model:value="modelRef.date_of_birth" type="datetime" />
          </n-form-item>


          <n-form-item path="email" label="Email">
            <n-input size="large" v-model:value="modelRef.email" @keydown.enter.prevent />
          </n-form-item>

          <n-form-item path="password" label="Password">
            <n-input show-password-on="click" size="large" v-model:value="modelRef.password" type="password"
              @input="handlePasswordInput" @keydown.enter.prevent />
          </n-form-item>

          <n-form-item ref="rPasswordFormItemRef" first path="reenteredPassword" label="Re-enter Password">
            <n-input show-password-on="click" size="large" v-model:value="modelRef.reenteredPassword"
              :disabled="!modelRef.password" type="password" @keydown.enter.prevent />
          </n-form-item>

          <n-checkbox v-model:checked="agreeTOS">
            I agree to the <a href="/terms-of-service" target="_blank">Terms of Service</a> and <a
              href="/privacy-policy" target="_blank">Privacy Policy</a>.
          </n-checkbox>

          <div class="button-wrapper">
            <n-button :loading="isLoading" style="width: 95%;" primary :disabled="modelRef.email === null"
              color="#8a2be2" round type="primary" @click="handleValidateButtonClick">
              Register
            </n-button>
          </div>

          <div class="divider">
            <span>or</span>
          </div>

          <div class="redirect-to-login">
            <p>Already have an account? <a href="#" @click.prevent="handleLoginRedirect">Log in</a></p>
          </div>

        </n-form>

      </n-card>
    </div>

  </div>


</template>




<script setup lang="ts">

import type {
  FormInst,
  FormItemInst,
  FormItemRule,
  FormRules,
  FormValidationError
} from 'naive-ui'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { globalAPI } from '../services'
import { AxiosError } from 'axios'
import { APIResponse } from '../services/axios_service/axiosTypes'
import { useUserStore } from '../stores/user_store';


interface ModelType {
  username: string | null
  email: string | null
  password: string | null
  reenteredPassword: string | null
  date_of_birth: string | null;
  name: string | null;
  surname: string | null;
}


const userStore = useUserStore()
const errorBox = ref({
  showError: false,
  errorMessage: ''
})
const router = useRouter()
const { mutateAsync, isPending } = globalAPI.userManagment.registerUser()
const formRef = ref<FormInst | null>(null)
const isLoading = ref(false)
const rPasswordFormItemRef = ref<FormItemInst | null>(null)
const agreeTOS = ref(false)
const modelRef = ref<ModelType>({
  username: null,
  email: null,
  password: null,
  reenteredPassword: null,
  date_of_birth: null,
  name: null,
  surname: null
})

function validatePasswordStartWith(rule: FormItemRule, value: string): boolean {
  return (
    !!modelRef.value.password
    && modelRef.value.password.startsWith(value)
    && modelRef.value.password.length >= value.length
  )
}

function validatePasswordSame(rule: FormItemRule, value: string): boolean {
  return value === modelRef.value.password
}

function validatePasswordLength(rule: FormItemRule, value: string): boolean {
  return value.length >= 8
}

function validateEmail(rule: FormItemRule, value: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(value);
}

const rules: FormRules = {
  username: [{
    required: true,
    message: 'Username is required'
  }],
  name: [{
    required: true,
    message: 'Name is required'
  }],
  surname: [{
    required: true,
    message: 'Surname is required'
  }],
  email: [{
    required: true,
    message: 'Email is required'
  },
  {
    validator: validateEmail,
    message: 'Invalid email format!',
    trigger: 'input'
  }
  ],
  date_of_birth: [{
    required: true,
    message: 'Date of Birth is required'
  }],
  password: [
    {
      required: true,
      message: 'Password is required'
    },
    {
      validator: validatePasswordLength,
      message: 'Password must be at least 8 characters long!',
      trigger: 'input'
    }
  ],
  reenteredPassword: [
    {
      required: true,
      message: 'Re-entered password is required',
      trigger: ['input', 'blur']
    },
    {
      validator: validatePasswordStartWith,
      message: 'Password is not same as re-entered password!',
      trigger: 'input'
    },
    {
      validator: validatePasswordSame,
      message: 'Password is not same as re-entered password!',
      trigger: ['blur', 'password-input']
    }
  ]
}

function handlePasswordInput() {
  if (modelRef.value.reenteredPassword) {
    rPasswordFormItemRef.value?.validate({ trigger: 'password-input' })
  }
}

function handleValidateButtonClick(e: MouseEvent) {
  e.preventDefault()
  isLoading.value = true
  formRef.value?.validate(async (errors: Array<FormValidationError> | undefined) => {

    if (!errors) {
      isLoading.value = true

      try {

        const date_of_birth = new Date(modelRef.value.date_of_birth!)
          .toISOString()
          .split("T")[0];


        const response = await mutateAsync({
          username: modelRef.value.username!,
          email: modelRef.value.email!,
          password: modelRef.value.password!,
          date_of_birth: date_of_birth,
          name: modelRef.value.name!,
          surname: modelRef.value.surname!
        })

        errorBox.value.showError = false
        errorBox.value.errorMessage = ''
        isLoading.value = false
        userStore.setEmail(modelRef.value.email!)
        router.push({
          name: "ConfirmEmail"
        })

      } catch (error) {
        let errorAxios = error as AxiosError<APIResponse<string>>
        errorBox.value.showError = true
        errorBox.value.errorMessage = errorAxios?.response?.data.response || 'An error occurred during login. Please try again.'
        isLoading.value = false
      }
    }
    else {
      console.log("Validation errors:", errors)
    }
  })
}

function handleLoginRedirect() {
  router.push({ name: 'Login' })
}

</script>



<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
}

.card-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 64px;
  padding-bottom: 64px;
}

.register-card {
  width: min(600px, 90%);
  border-radius: 16px;
  box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.2);
}

.register-header h1 {
  font-size: 28px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 24px;
}

.button-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  width: 100%;
}

.login-link-wrapper {
  display: flex;
  flex-direction: row;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: #888;
  font-size: 14px;
  margin: 32px 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #ccc;
}

.divider span {
  padding: 0 12px;
}

.redirect-to-login {
  text-align: center;
  margin-top: 16px;
  width: 100%;
}

.error-box {
  background-color: #ede5e5;
  text-align: center;
  border: 1px solid #ff4d4f;
  padding: 8px;
  margin-bottom: 16px;
  border-radius: 4px;
}
</style>
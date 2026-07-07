<template>
    <div class="root-profile">

        <div class="warning-class" v-if="!userStore.hasEmbedKey || !userStore.hasLLmKey || !userStore.hasPineconeKey">

            <div v-if="!userStore.hasEmbedKey">
                <h4>Warning:</h4>
                <p>{{ userStore.hasEmbedKey? '' : 'Please insert one of the following keys [Gemini, Jina, Cohere] to use embed features.' }}</p>
            </div>

            <div v-if="!userStore.hasLLmKey">
                <h4>Warning:</h4>
                <p>{{ userStore.hasLLmKey? '' : 'Please insert one of the following keys [Gemini, Groq, Mistral] to use evaluation and chatbot features.' }}</p>
            </div>

            <div v-if="!userStore.hasPineconeKey">
                <h4>Warning:</h4>
                <p>{{ userStore.hasPineconeKey? '' : 'Please insert one of the following keys [Pinecone] to use pinecone vector db features.' }}</p>
            </div>
        </div>

        <n-card class="user-name-surname">

            <div>
                <h4>Username:</h4>
                <p>{{ userStore.userInfo?.username }}</p>
            </div>

            <div>
                <h4>Name:</h4>
                <p>{{ userStore.userInfo?.name }}</p>
            </div>

            <div>
                <h4>Surname:</h4>
                <p>{{ userStore.userInfo?.surname }}</p>
            </div>
        </n-card>


        <n-card class="user-info">
            <div>
                <h4>Email:</h4>
                <p>{{ userStore.userInfo?.email }}</p>
            </div>

            <div>
                <h4>Date of birth:</h4>
                <p>{{ userStore.userInfo?.date_of_birth }}</p>
            </div>

            <div>
                <h4>User Role:</h4>
                <p>{{ userStore.userInfo?.user_classification }}</p>
            </div>
        </n-card>



        <n-card class="api-keys">
            <div>
                <div class="key-header">
                    <h4>Groq API Key:</h4>
                    <div :class="userStore.userInfo?.api_keys?.has_groq_api_key ? 'api-key-bound' : 'api-key-unbound'">
                        {{ userStore.userInfo?.api_keys?.has_groq_api_key ? 'Present' : 'Missing' }}
                    </div>
                </div>
                <div class="api-key-modify">
                    <button class="update-button" @click="handleKeyUpdate('groq_api_key')"> {{
                        userStore.userInfo?.api_keys?.has_groq_api_key ? 'Update' : 'Insert' }} </button>
                    <button class="delete-button" :disabled="!userStore.userInfo?.api_keys?.has_groq_api_key || deletingKeys['groq_api_key']" @click="handleKeyDeletion('groq_api_key')"> Delete </button>
                </div>
            </div>

            <div>
                <div class="key-header">
                    <h4>Gemini API Key:</h4>
                    <div
                        :class="userStore.userInfo?.api_keys?.has_gemini_api_key ? 'api-key-bound' : 'api-key-unbound'">
                        {{ userStore.userInfo?.api_keys?.has_gemini_api_key ? 'Present' : 'Missing' }}
                    </div>
                </div>
                <div class="api-key-modify">
                    <button class="update-button" @click="handleKeyUpdate('gemini_api_key')"> {{
                        userStore.userInfo?.api_keys?.has_gemini_api_key ? 'Update' : 'Insert' }} </button>
                    <button class="delete-button" :disabled="!userStore.userInfo?.api_keys?.has_gemini_api_key || deletingKeys['gemini_api_key']" @click="handleKeyDeletion('gemini_api_key')"> Delete </button>
                </div>
            </div>

            <div>
                <div class="key-header">
                    <h4>Mistral API Key:</h4>
                    <div
                        :class="userStore.userInfo?.api_keys?.has_mistral_api_key ? 'api-key-bound' : 'api-key-unbound'">
                        {{ userStore.userInfo?.api_keys?.has_mistral_api_key ? 'Present' : 'Missing' }}
                    </div>
                </div>
                <div class="api-key-modify">
                    <button class="update-button" @click="handleKeyUpdate('mistral_api_key')"> {{
                        userStore.userInfo?.api_keys?.has_mistral_api_key ? 'Update' : 'Insert' }} </button>
                    <button class="delete-button" :disabled="!userStore.userInfo?.api_keys?.has_mistral_api_key || deletingKeys['mistral_api_key']" @click="handleKeyDeletion('mistral_api_key')"> Delete </button>
                </div>
            </div>

            <div>
                <div class="key-header">
                    <h4>Jina API Key:</h4>
                    <div :class="userStore.userInfo?.api_keys?.has_jina_api_key ? 'api-key-bound' : 'api-key-unbound'">
                        {{ userStore.userInfo?.api_keys?.has_jina_api_key ? 'Present' : 'Missing' }}
                    </div>
                </div>
                <div class="api-key-modify">
                    <button class="update-button" @click="handleKeyUpdate('jina_api_key')"> {{
                        userStore.userInfo?.api_keys?.has_jina_api_key ? 'Update' : 'Insert' }} </button>
                    <button class="delete-button" :disabled="!userStore.userInfo?.api_keys?.has_jina_api_key || deletingKeys['jina_api_key']" @click="handleKeyDeletion('jina_api_key')"> Delete </button>
                </div>
            </div>


            <div>
                <div class="key-header">
                    <h4>Cohere API Key:</h4>
                    <div
                        :class="userStore.userInfo?.api_keys?.has_cohere_api_key ? 'api-key-bound' : 'api-key-unbound'">
                        {{ userStore.userInfo?.api_keys?.has_cohere_api_key ? 'Present' : 'Missing' }}
                    </div>
                </div>
                <div class="api-key-modify">
                    <button class="update-button" @click="handleKeyUpdate('cohere_api_key')"> {{
                        userStore.userInfo?.api_keys?.has_cohere_api_key ? 'Update' : 'Insert' }} </button>
                    <button class="delete-button" :disabled="!userStore.userInfo?.api_keys?.has_cohere_api_key || deletingKeys['cohere_api_key']" @click="handleKeyDeletion('cohere_api_key')"> Delete </button>
                </div>
            </div>


            <div>
                <div class="key-header">
                    <h4>Pinecone API Key:</h4>
                    <div
                        :class="userStore.userInfo?.api_keys?.has_pinecone_api_key ? 'api-key-bound' : 'api-key-unbound'">
                        {{ userStore.userInfo?.api_keys?.has_pinecone_api_key ? 'Present' : 'Missing' }}
                    </div>
                </div>
                <div class="api-key-modify">
                    <button class="update-button" @click="handleKeyUpdate('pine_cone_api_key')"> {{
                        userStore.userInfo?.api_keys?.has_pinecone_api_key ? 'Update' : 'Insert' }} </button>
                    <button class="delete-button" :disabled="!userStore.userInfo?.api_keys?.has_pinecone_api_key || deletingKeys['pine_cone_api_key']" @click="handleKeyDeletion('pine_cone_api_key')"> Delete </button>
                </div>
            </div>

            <n-modal v-model:show="showModal">
                <n-card style="max-width: 600px" title="" :bordered="false" size="huge" role="dialog" 
                    class="modal-card">
                    <div class="api-message">Update {{ showModalData.message }}:</div>



                    <n-form ref="formRef" inline :label-width="80" :model="formValue" :rules="rules" >
                        <n-form-item label="" path="api_key">
                            <n-input v-model:value="formValue.api_key" large placeholder="Input Api Key" />
                        </n-form-item>
                        <n-form-item>
                            <n-button :loading="isLoading" @click="handleApiReqClick(showModalData.key_type, formValue.api_key)">
                                Submit
                            </n-button>
                        </n-form-item>
                    </n-form>


                </n-card>
            </n-modal>

        </n-card>

    </div>
</template>


<script setup lang="ts">
import { ref } from 'vue';
import { globalAPI } from '../services';
import { useUserStore } from '../stores/user_store';
import { FormInst } from 'naive-ui';


const userStore = useUserStore()
const deletingKeys = ref<Record<string, boolean>>({
    groq_api_key: false,
    gemini_api_key: false,
    mistral_api_key: false,
    jina_api_key: false,
    cohere_api_key: false,
    pine_cone_api_key: false,
})

const keyMessages: Record<string, string> = {
    groq_api_key: "Groq API Key",
    gemini_api_key: "Gemini API Key",
    mistral_api_key: "Mistral API Key",
    jina_api_key: "Jina API Key",
    cohere_api_key: "Cohere API Key",
    pine_cone_api_key: "Pinecone API Key",
};

function handleKeyUpdate(key_type: string) {
    showModal.value=true
    showModalData.value.key_type = key_type
    showModalData.value.message = keyMessages[key_type] ?? "API Key";
}

const showModal = ref(false)
const showModalData = ref({
    "key_type": "",
    "message": ""
})

const { mutateAsync: deleteApiKey } = globalAPI.userManagment.deleteKey()
const { mutateAsync: updateApiKey } = globalAPI.userManagment.updateKey()

async function handleKeyDeletion(key_type: string) {
    if (deletingKeys.value[key_type]) return
    deletingKeys.value[key_type] = true
    try {
        const response = await deleteApiKey({ key_type: key_type })
        console.log(response)
    } finally {
        deletingKeys.value[key_type] = false
    }

}


const formRef = ref<FormInst | null>(null)
const formValue = ref({
    api_key: ''
})

const rules = {

    api_key: {
        required: true,
        message: 'Please input your api key',
        trigger: 'blur'
    },
}


const isLoading = ref(false)
async function handleApiReqClick(key_type: string, api_key: string) {
    isLoading.value = true
    const reponse = await updateApiKey({
        key_type: key_type,
        api_key: api_key
    })
    isLoading.value = false
    showModal.value = false
    showModalData.value.key_type = ""
    showModalData.value.message = ""
}

</script>


<style scoped>
.root-profile {
    display: flex;
    flex-direction: column;
    gap: 32px;
    height: 100vh;
}

.user-name-surname :deep(.n-card-content) {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
}

.user-info :deep(.n-card-content) {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
}

.api-keys {
    min-height: 500px;
}

.api-keys :deep(.n-card-content) {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
}

.api-keys :deep(.n-card-content > div) {
    width: 350px;
}

.api-key-modify {
    display: flex;
    gap: 12px;
    flex-direction: row;
}

.api-key-unbound {
    color: red;
    font-weight: 700;
    font-size: 16px;
}

.api-key-bound {
    color: green;
    font-weight: 600;
    font-size: 18px;
}

.api-keys :deep(.n-card-content > div) {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.key-header{
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    gap: 16px;
}

.update-button,
.delete-button {
    padding: 8px 16px;
    border: none;
    border-radius: 16px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s ease, transform 0.15s ease;
}

.update-button {
    background-color: #2563eb;
    color: white;
}

.update-button:hover {
    background-color: #1d4ed8;
}

.update-button:active {
    transform: scale(0.98);
}

.delete-button {
    background-color: #dc2626;
    color: white;
}

.delete-button:hover {
    background-color: #b91c1c;
}

.delete-button:active {
    transform: scale(0.98);
}

.warning-class{
    border-color: #b91c1c;
    background-color: #f5b2b2;
    color: #b91c1c;
    border: 2px solid;
    border-radius: 8px;
    padding: 32px;
}

.warning-class h3{
    font-weight: 600;
}

.warning-class div {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
}

.delete-button:disabled {
    background-color: #f3a6a6;
    cursor: not-allowed;
    opacity: 0.7;
}

.api-message{
    font-weight: 600;
    font-size: 18px;
    font-family: Arial, Helvetica, sans-serif;
    letter-spacing: 0.02em;
}

@media (max-width: 1200px) {
.api-keys :deep(.n-card-content) {
    display: flex;
    flex-direction: column;
    gap:32px;
    justify-content: center;
    align-items: center;
}

.user-name-surname :deep(.n-card-content) {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.user-info :deep(.n-card-content) {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.user-name-surname :deep(.n-card-content) {
    text-align: center;
}

.user-info :deep(.n-card-content) {
 text-align: center;
}

}
</style>
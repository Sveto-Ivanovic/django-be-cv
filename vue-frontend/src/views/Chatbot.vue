<template>

    <div class="chatbot-wrapper" v-if="isSuccessHist">

        <div class="chatbot-screen-wrapper">

            <div class="chatbot-screen">
                <div v-for="value in messages" class="qa_item">
                    <div class="question">{{ value.question }}</div>
                    <div class="answer">
                        <div v-if="value.answer && value.answer !== '' && value.answer !== null">
                            {{ value.answer ? value.answer : '' }}
                        </div>
                        <QALoader circle_size="20px" v-else-if="value.question && value.question !== ''"></QALoader>
                    </div>

                </div>

            </div>


            <div class="seperator_qa"></div>

        </div>

        <div class="option-buttons">
            <div class="options">
                <button @click="toggleModal">
                    <n-icon size="15">
                        <Options />
                    </n-icon>
                </button>
            </div>
            <div class="options">
                <button @click="newChat">
                    <n-icon size="25">
                        <Add />
                    </n-icon>
                </button>
            </div>
        </div>


        <div class="chatbot-input">
            <textarea v-model="query" placeholder="Ask question ..." @keydown.enter.exact.prevent
                @keydown.enter.exact="handleEnter" @keydown.enter.shift.exact="handleShiftEnter"></textarea>
            <button @click="handleSendMessage">
                <n-icon size="15">
                    <Send />
                </n-icon>
            </button>

        </div>
    </div>
    <div class="loader" v-else-if="isFetchingHist">
        <LoadingComponent></LoadingComponent>
    </div>
    <div class="error-event" v-else-if="isFetchedHist && isErrorHist"> Error occured ...</div>



    <n-modal v-model:show="showModal">
        <n-card style="max-width: 800px" title="" :bordered="false" size="huge" role="dialog" class="modal-wrapper">

            <div class="chat-history-wrapper">
                <h2>Chat history</h2>
                <div class="seperator"></div>

                <div class="chat-history">
                    <div class="chat-history-item"
                        :class="value.id === conversation_id ? 'chat-history-item-active ' : 'chat-history-item-inactive '"
                        v-for="value in history_simulation" @click="setConvId(value.id)" :title="value.name">
                        {{ value.name }}
                    </div>

                </div>
            </div>

            <div class="seperator"></div>

            <div class="chose-model">
                Chose Model:
                <n-select v-model:value="selectedModel" :options="llmModelOptions" />

            </div>


        </n-card>
    </n-modal>
</template>


<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { Send, Options, Add } from '@vicons/ionicons5'
import { useUserStore } from '../stores/user_store';
import QALoader from '../components/QALoader.vue';
import { globalAPI } from '../services';
import LoadingComponent from '../components/LoadingComponent.vue';
import { ChatbotRequest, ChatbotResponse } from '../services/chatbot/types';

const conversation_id = ref("")
const query = ref('')
const showModal = ref(false)
const userStore = useUserStore()
const selectedModel = ref('')
const llmModelOptions = computed(() => {

    let options = []
    if (userStore.userInfo?.api_keys.has_gemini_api_key) {
        options.push(
            {
                label: 'gemini-2.5-flash',
                value: 'gemini-2.5-flash',
            }
        )
        options.push(
            {
                label: 'gemini-3.5-flash',
                value: 'gemini-3.5-flash',
            }
        )

    }
    if (userStore.userInfo?.api_keys.has_groq_api_key) {
        options.push(
            {
                label: 'llama-3.3-70b-versatile',
                value: 'llama-3.3-70b-versatile',
            }
        )
    }
    if (userStore.userInfo?.api_keys.has_mistral_api_key) {
        options.push(
            {
                label: 'mistral-small-latest',
                value: 'mistral-small-latest',
            }
        )
    }
    return options

})
const { data, isFetched, isFetching, isSuccess, seedMessages } = globalAPI.userChatbot.getChatMessages(computed(() => ({ conv_id: conversation_id.value })))
const { data: dataHist, isFetched: isFetchedHist, isFetching: isFetchingHist, isSuccess: isSuccessHist, isError: isErrorHist } = globalAPI.userChatbot.getChatbotHistory()
const { mutateAsync: callChatbot } = globalAPI.userChatbot.callChatbot()

const history_simulation = computed(() => {
    console.log(dataHist.value?.data.response)
    if (dataHist.value?.data.response && typeof dataHist.value?.data.response !== 'string') { return dataHist.value?.data.response ?? [] }

})

interface QAItem {
    created_at?: string | null
    question: string
    answer?: string | null
}

const messages = ref<QAItem[]>([])

watch(data, (newVal) => {
    if (conversation_id.value === '') {
        messages.value = []
        return
    }
    if (newVal?.data.response && typeof newVal.data.response !== 'string') {
        messages.value = newVal.data.response
    } else {
        messages.value = []
    }
}, { immediate: true })

watch(
    llmModelOptions,
    (newOptions) => {
        if (newOptions.length && !selectedModel.value) {
            selectedModel.value = newOptions[0].value
        }
    },
    { immediate: true }
)

function setConvId(id: string) {
    conversation_id.value = id
}

function toggleModal() {
    showModal.value = true
}

function handleEnter(e: KeyboardEvent) {
    e.preventDefault()
    handleSendMessage()
}

function handleShiftEnter(e: KeyboardEvent) {
    e.preventDefault()
    query.value = query.value + '\n'
}


async function handleSendMessage() {
    console.log(query)
    if (query.value.trim() === '') {
        alert("Query cant be empty")
        return

    }

    let data: ChatbotRequest = {
        question: query.value,
        llm_model: selectedModel.value
    }
    messages.value.push({
        question: query.value
    })

    if (conversation_id.value !== '') {
        data['conv_id'] = conversation_id.value
    }

    try {
        const response = await callChatbot(data)
        console.log(response)

        const lenofMessages = messages.value.length
        if (typeof response.data.response === 'object') {
            messages.value[lenofMessages - 1]['answer'] = response.data.response.response
        }

        if (conversation_id.value === '' && typeof response.data.response === 'object' && response.data.response?.conv_id) {
            seedMessages(response.data.response?.conv_id, {
                data: {
                    response: messages.value.map(m => ({
                        question: m.question,
                        answer: m.answer ?? '',
                        created_at: new Date().toISOString()
                    })),
                    res_status: 'success'
                }
            } as any)
            conversation_id.value = response.data.response?.conv_id
        }


    }
    catch (e) {
        console.log(e)
    }

}

function newChat() {
    conversation_id.value = ""
}



</script>


<style scoped>
.loader {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.error-event {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding-top: 32px;
    font-weight: 600;
    font-size: 24px;
    color: red;
    font-family: 'Times New Roman', Times, serif;
    letter-spacing: 0.01em;
}

.chatbot-wrapper {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

}

.chatbot-input {
    min-height: 52px;
    width: min(80%, 800px);
    border: 1px solid #cfcfcf;
    border-radius: 24px;
    transition: border-color .2s;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;


}

.chatbot-input:focus-within {
    border-color: #888;
}

.chatbot-input button {
    width: 38px;
    height: 38px;
    margin: 6px;
    border: none;
    border-radius: 50%;
    background: #111;
    color: white;
    cursor: pointer;
    transition: background-color .2s;
}

.chatbot-input button:hover {
    background-color: rgb(221, 221, 213);
}


.chatbot-input textarea {
    border-radius: 16px;
    height: 48px;
    line-height: 1.5;
    padding-left: 16px;
    padding-top: 14px;
    flex: 1;
    border: none;
    outline: none;
    box-shadow: none;
    resize: none;
    overflow-y: hidden;
    background: transparent;
}

.option-buttons {
    display: flex;
    flex-direction: row;
    gap: 16px
}

.options {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
}

.options button {
    border-radius: 50%;
    height: 35px;
    width: 35px;
    background-color: #888;
    color: white;
    opacity: 0.3;
    transition: opacity 0.2 ease;
    cursor: pointer;
    border: none;
}

.options button:hover {
    opacity: 1;
}

.chat-history {
    width: 100%;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 4px;
    height: 400px;
    padding: 8px 4px;
}

.chat-history-item {
    flex-shrink: 0;
    cursor: pointer;
    max-width: min(90%, 600px);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 14px;
    font-weight: 500;
    height: 30px;
    font-family: inherit;
    letter-spacing: 0.01em;
    padding: 10px 12px;
    border-radius: 10px;
    border-left: 3px solid transparent;
    transition: background-color 0.15s ease, border-color 0.15s ease;
}


.chat-history-item-inactive {
    color: #333;
}

.chat-history-item-inactive:hover {
    background-color: #f2f2f2;
}

.chat-history-item-active {
    background-color: #eef2ff;
    border-left-color: #4f6bff;
    color: #1e293b;
}

.modal-wrapper :deep(.n-card-content) {
    width: 100%;
    flex: 1;
    min-height: 0;
    overflow: hidden;
}

.chose-model {
    padding-top: 16px;
}

.seperator {
    height: 2px;
    border-bottom: 2px solid #888;
}

.chatbot-screen-wrapper {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.chatbot-screen {
    height: 80vh;
    width: min(1200px, 90%);
    overflow-y: auto;
    padding-bottom: 8px;
}

.qa_item {
    display: flex;
    flex-direction: column;
    padding-top: 16px;
    gap: 32px
}

.question {
    align-self: end;
    background-color: #4f6bff;
    color: #fff;
    border-radius: 16px 16px 4px 16px;
    max-width: min(300px, 78%);
    margin-left: 20%;
    padding: 10px 14px;
}

.answer {
    align-self: start;
    background-color: #f1f1f1;
    color: #1e1e1e;
    border-radius: 16px 16px 16px 4px;
    max-width: min(500px, 78%);
    margin-right: 20%;
    padding: 10px 14px;
}

.seperator_qa {
    height: 2px;
    border-bottom: 2px solid #888;
    width: min(1200px, 90%);

}
</style>
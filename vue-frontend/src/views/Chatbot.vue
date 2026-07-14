<template>

    <div class="chatbot-wrapper" v-if="isSuccessHist">

        <div class="chatbot-screen-wrapper">

            <div class="chatbot-screen">
                <div class="start-new-chat" v-if="messages.length === 0">
                    Hello {{ userStore.userInfo?.name }} what question do you have for me?
                </div>
                <div v-for="value in messages" class="qa_item">
                    <div class="question">{{ value.question }}</div>
                    <div v-if="value.answer && value.answer !== '' && value.answer !== null" class="answer">
                        <div>
                            {{ value.answer ? value.answer : '' }}
                        </div>
                    </div>
                    <QALoader circle_size="20px" v-if="value.answer === undefined || value.answer === null"></QALoader>

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
            <button @click="handleSendMessage" :class="isDisabled ? 'btn-disabled' : ''">
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
                <label class="field-label">Chose Model</label>
                <n-select v-model:value="selectedModel" :options="llmModelOptions" />



            </div>

            <div class="seperator"></div>

            <div class="rag-config-wrapper">
                <div class="form-section">
                    <div class="field">
                        <label class="field-label">Vector Store Settings</label>
                        <n-radio-group v-model:value="selectVectorStore" name="vectorStoreGroup" class="radio-group">
                            <n-space>
                                <n-radio value="supabase">Supabase</n-radio>
                                <n-radio value="pinecone">Pinecone</n-radio>
                            </n-space>
                        </n-radio-group>
                    </div>

                    <div v-if="selectVectorStore === 'supabase'">
                        <div class="inline-fields indented-field">
                            <div class="field">
                                <label class="field-label">Select Namespace</label>
                                <n-select v-model:value="supabaseNamespaceSelected" placeholder="Select Namespace:"
                                    :options="namespaceOptions" />
                            </div>

                            <div class="field half-width">
                                <label class="field-label">Top K</label>
                                <n-input v-model:value="supabaseTopK" placeholder="0" />
                            </div>
                        </div>

                        <div class="inline-fields indented-field">
                            <div class="field">
                                <label class="field-label">Select Mode</label>
                                <n-select v-model:value="supabaseMode" placeholder="Select Mode:"
                                    :options="modeOptions" />
                            </div>

                            <div class="field">
                                <label class="field-label">Semantic Search Mode:</label>
                                <n-select v-model:value="supabaseSemanticSearchMode" placeholder="Semantic Search Mode:"
                                    :options="semanticSearchOptions" />
                            </div>
                        </div>
                    </div>

                    <div v-if="selectVectorStore === 'pinecone'">
                        <div class="inline-fields indented-field">
                            <div class="field">
                                <label class="field-label">Select Index Name:</label>
                                <n-select v-model:value="pineconeIndexNameSelected" placeholder="Select Index Name:"
                                    :options="indexOptionsDense" />
                            </div>

                            <div class="field half-width">
                                <label class="field-label">Top K</label>
                                <n-input v-model:value="pineconeTopK" placeholder="0" />
                            </div>
                        </div>

                        <div class="inline-fields indented-field">
                            <div class="field">
                                <label class="field-label">Select Mode</label>
                                <n-select v-model:value="pineconeMode" placeholder="Select Mode:"
                                    :options="modeOptions" />
                            </div>

                            <div class="field" v-if="pineconeMode !== 'semantic'">
                                <label class="field-label">Input Lexical Index Name</label>
                                <n-select v-model:value="pineconeLexicalIndexName" placeholder="Select Lexical Index:"
                                    :options="indexOptionsLexical" />
                            </div>
                        </div>
                    </div>
                </div>

                <div class="form-section">
                    <h3 class="section-title">Fetch Neighbor Settings</h3>

                    <div class="field">
                        <label class="field-label">Fetch Neighbors:</label>
                        <n-radio-group v-model:value="includeNeighbors" name="neighborsGroup" class="radio-group">
                            <n-space>
                                <n-radio value="yes">Yes</n-radio>
                                <n-radio value="no">No</n-radio>
                            </n-space>
                        </n-radio-group>
                    </div>

                    <div v-if="includeNeighbors === 'yes'">
                        <div class="field indented-field">
                            <label class="field-label">Get All Chunks</label>
                            <n-select v-model:value="getAllNeighborChunks" placeholder=""
                                :options="fetchAllChunksOptions" />
                        </div>

                        <div class="field indented-field">
                            <label class="field-label">Nearest Num. of Chunks</label>
                            <n-input v-model:value="nearestChunksN" placeholder="" />
                        </div>

                        <div class="field indented-field">
                            <label class="field-label">Fetch Neighbor Pages</label>
                            <n-input v-model:value="nearestPageOrArrayMembersN" placeholder="" />
                        </div>
                    </div>
                </div>

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
import { ChatbotRequest, ChatbotResponse, NearestNeighborSetting } from '../services/chatbot/types';

const conversation_id = ref("")
const query = ref('')
const showModal = ref(false)
const userStore = useUserStore()
const selectedModel = ref('')
const isDisabled = ref(false)

const selectVectorStore = ref('supabase')
const supabaseNamespaceSelected = ref(null)
const supabaseTopK = ref('3')
const supabaseMode = ref(null)
const supabaseSemanticSearchMode = ref(null)

const pineconeIndexNameSelected = ref(null)
const pineconeTopK = ref('3')
const pineconeMode = ref(null)
const pineconeLexicalIndexName = ref(null)

const includeNeighbors = ref('no')
const getAllNeighborChunks = ref('no')
const nearestChunksN = ref('0')
const nearestPageOrArrayMembersN = ref('0')

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
const namespaceOptions = userStore.userInfo?.supabase_namespaces_names.map(
    v => ({
        label: v,
        value: v
    })
)

const modeOptions = ['semantic', 'hybrid', 'lexical'].map(
    v => ({
        label: v,
        value: v
    })
)

const fetchAllChunksOptions = ['yes', 'no'].map(
    v => ({
        label: v,
        value: v
    })
)

const semanticSearchOptions = ['cosine', 'euclidean', 'inner_product'].map(
    v => ({
        label: v,
        value: v
    })
)

console.log(userStore.userInfo)
const indexOptionsDense = computed(() => {
    const denseOptions = userStore.userInfo?.pinecone_indexes
        .filter((item) => item.model !== "None")
        .map((item) => ({
            label: item.name,
            value: item.name
        }))
    return denseOptions
})

const indexOptionsLexical = computed(() => {
    const lexicalOptions = userStore.userInfo?.pinecone_indexes
        .filter((item) => item.model === "None")
        .map((item) => ({
            label: item.name,
            value: item.name
        }))
    return lexicalOptions
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
        messages.value = JSON.parse(JSON.stringify(newVal.data.response))
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
    // check if we have query
    isDisabled.value = true
    console.log(query)
    if (query.value.trim() === '') {
        alert("Query cant be empty")
        isDisabled.value = false
        return

    }

    // manage states
    let data: ChatbotRequest = {
        question: query.value,
        llm_model: selectedModel.value
    }
    messages.value.push({
        question: query.value
    })
    query.value = ''

    if (conversation_id.value !== '') {
        data['conv_id'] = conversation_id.value
    }

    let neighbor_config: NearestNeighborSetting | undefined = undefined
    if (includeNeighbors.value === 'yes') {

        neighbor_config = {
            get_all_neighbor_chunks: getAllNeighborChunks.value === 'yes' ? true : false,
            nearest_chunks_n:  !Number.isNaN(nearestChunksN.value) && Number(nearestChunksN.value) >= 0  ? Number(nearestChunksN.value) : 0,
            nearest_page_or_array_members_n: !Number.isNaN(nearestPageOrArrayMembersN.value) && Number(nearestPageOrArrayMembersN.value) >= 0 ? Number(nearestPageOrArrayMembersN.value) : 0,

        }
    }


    // supabase & pinecone configs
    if (selectVectorStore.value === 'supabase' && supabaseNamespaceSelected.value !== null) {
        const model = userStore.userInfo?.supabase_namespaces.filter(item => item.name == supabaseNamespaceSelected.value)[0].model
        if (model === undefined) {
            console.log("Undefined mode")
            return
        }

        let tableName;

        if (model === "gemini-embedding-001") {
            tableName = "vector_search_3072";
        } else if (model === "jina-embeddings-v4") {
            tableName = "vector_search_2048";
        } else if (model === "embed-v4.0") {
            tableName = "vector_search_1536";
        } else {
            console.log('invalid model')
            return
        }
        data['supabase_metadata'] = {
            namespace: supabaseNamespaceSelected.value,
            top_k: !Number.isNaN(supabaseTopK.value) && Number(supabaseTopK.value) >= 3 ? Number(supabaseTopK.value) : 3,
            mode: supabaseMode.value ?? 'semantic',
            semantic_search_mode: supabaseSemanticSearchMode.value ?? 'cosine',
            table_name: tableName,
            model: model,
            nearest_neighbor_settings: neighbor_config
        }
    }
    else if (selectVectorStore.value === 'pinecone' && pineconeIndexNameSelected.value !== null) {
        console.log(pineconeIndexNameSelected.value)
        const model = userStore.userInfo?.pinecone_indexes.filter(item => item.name == pineconeIndexNameSelected.value)[0].model
        if (model === undefined) {
            console.log("Undefined mode")
            return
        }
        console.log(model)
        data['pinecone_metadata'] = {
            index_name: pineconeIndexNameSelected.value,
            top_k:!Number.isNaN(pineconeTopK.value)&& Number(pineconeTopK.value) >= 3  ? Number(pineconeTopK.value) : 3,
            mode: supabaseMode.value ?? 'semantic',
            index_name_lexical: pineconeLexicalIndexName.value !== null ? pineconeLexicalIndexName.value : undefined,
            model: model,
            nearest_neighbor_settings: neighbor_config
        }
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
        isDisabled.value = false


    }
    catch (e) {
        isDisabled.value = false
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

.modal-wrapper {
    overflow-y: auto;
    height: min(800px, 90vh);
    overflow-x: hidden;
}

.modal-wrapper :deep(.n-card-content) {
    width: 100%;
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 16px;
    height: min(800px, 90vh);

}

.chose-model {
    padding-top: 16px;
    padding-bottom: 16px;

}

.seperator {
    height: 2px;
    border-bottom: 2px solid #888;
}

.chatbot-screen-wrapper {
    display: flex;
    flex-direction: column;
    justify-content: center;
    width: 100%;
    align-items: center;
}

.chatbot-screen {
    height: 80vh;
    width: min(800px, 90%);
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
    max-width: min(350px, 78vh);
    margin-left: 20%;
    padding: 10px 14px;
        white-space: pre-wrap;
    overflow-wrap: break-word;
}

.answer {
    align-self: start;
    background-color: #f1f1f1;
    color: #1e1e1e;
    border-radius: 16px 16px 16px 4px;
    max-width: min(600px, 78vh);
    margin-right: 20%;
    padding: 10px 14px;
        white-space: pre-wrap;
    overflow-wrap: break-word;
}

.seperator_qa {
    height: 2px;
    border-bottom: 2px solid #888;
    width: min(800px, 90%);

}

.btn-disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
}

.start-new-chat {
    text-align: center;
    padding: 64px;
    font-size: 32px;
    font-weight: 500;
    background: linear-gradient(90deg, rgba(72, 23, 145, 1) 0%, rgba(9, 9, 121, 1) 35%, rgba(0, 212, 255, 1) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    -webkit-text-fill-color: transparent;
}

.rag-config-wrapper {
    display: flex;
    flex-direction: column;
    gap: 24px;
    width: 100%;
    max-height: 70vh;
    overflow-y: auto;
    padding: 4px 16px;
    box-sizing: border-box;
}

.form-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.section-title {
    margin: 0 0 4px 0;
    font-size: 15px;
    font-weight: 600;
}

.field {
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex: 1;
    min-width: 0;
}

.field-label {
    font-size: 13px;
    font-weight: 500;
    opacity: 0.85;
}

.radio-group {
    display: flex;
}

.inline-fields {
    display: flex;
    gap: 16px;
    width: 100%;
}

.indented-field {
    padding-left: 12px;
    border-left: 2px solid rgba(128, 128, 128, 0.2);
    margin-top: 4px;
}

.half-width {
    flex: 0 0 30%;
    max-width: 30%;
}


@media (max-width: 640px) {
    .inline-fields {
        flex-direction: column;
        gap: 12px;
    }

    .half-width {
        max-width: 100%;
        flex: 1;
    }

    .indented-field {
        padding-left: 8px;
    }

    .rag-config-wrapper {
        max-height: 75vh;
        gap: 20px;
    }
}

@media(max-width: 800px) {
    .start-new-chat {
        font-size: 18px;

    }
}
</style>
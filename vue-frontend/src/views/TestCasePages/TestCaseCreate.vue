<template>
    <n-form class="form-class embed-form" ref="formRef" label-placement="top" :label-width="80" :model="formValue"
        :rules="rules">

        <div class="form-section">
            <h3 class="section-title">Evaluate Benchmark</h3>

            <n-form-item label="Input Testcase Name" path="input_testcase_name" class="form-item indented-field">
                <n-input v-model:value="formValue.input_testcase_name" placeholder="mytestcase-x" />
            </n-form-item>

            <n-form-item label="Select QA Model" path="qa_model" class="form-item">
                <n-select v-model:value="formValue.qa_model" placeholder="Select QA Model:"
                    :options="llmModelOptions" />
            </n-form-item>

            <n-form-item label="Select Evaluation Model" path="eval_model" class="form-item">
                <n-select v-model:value="formValue.eval_model" placeholder="Select Evaluation Model:"
                    :options="llmModelOptions" />
            </n-form-item>

        </div>

        <div class="form-section">
            <h3 class="section-title">Chunking</h3>

            <n-form-item label="Vector Store Settings" path="select_vector_store" class="form-item">
                <n-radio-group v-model:value="formValue.select_vector_store" name="radiogroup2" class="radio-group">
                    <n-space>
                        <n-radio value="supabase">Supabase</n-radio>
                        <n-radio value="pinecone">Pinecone</n-radio>
                    </n-space>
                </n-radio-group>
            </n-form-item>

            <div v-if="formValue.select_vector_store == 'supabase'">
                <div class="inline-fields indented-field">
                    <n-form-item label="Select Namespace" path="supabase.namespace_selected" class="form-item">
                        <n-select v-model:value="formValue.supabase.namespace_selected" placeholder="Select Namespace:"
                            :options="namespaceOptions" />
                    </n-form-item>

                    <n-form-item label="Top K" path="supabase.top_k" class="form-item half-width">
                        <n-input v-model:value="formValue.supabase.top_k" placeholder="0" />
                    </n-form-item>
                </div>

                <div class="inline-fields indented-field">
                    <n-form-item label="Select Mode" path="supabase.mode" class="form-item">
                        <n-select v-model:value="formValue.supabase.mode" placeholder="Select Mode:"
                            :options="modeOptions" />
                    </n-form-item>

                    <n-form-item label="Semantic Search Mode:" path="supabase.semantic_search_mode" class="form-item">
                        <n-select v-model:value="formValue.supabase.semantic_search_mode"
                            placeholder="Semantic Search Mode:" :options="semanticSearchOptions" />
                    </n-form-item>
                </div>
            </div>

            <div v-if="formValue.select_vector_store == 'pinecone'">
                <div class="inline-fields indented-field">
                    <n-form-item label="Select Index Name:" path="pinecone.index_name_selected" class="form-item">
                        <n-select v-model:value="formValue.pinecone.index_name_selected"
                            placeholder="Select Index Name:" :options="indexOptionsDense" />
                    </n-form-item>

                    <n-form-item label="Top K" path="pinecone.top_k" class="form-item half-width">
                        <n-input v-model:value="formValue.pinecone.top_k" placeholder="0" />
                    </n-form-item>
                </div>

                <div class="inline-fields indented-field">
                    <n-form-item label="Select Mode" path="pinecone.mode" class="form-item">
                        <n-select v-model:value="formValue.pinecone.mode" placeholder="Select Mode:"
                            :options="modeOptions" />
                    </n-form-item>

                    <n-form-item label="Input Lexical Index Name" v-if="formValue.pinecone.mode != 'semantic'"
                        path="pinecone.lexical_index_name" class="form-item">
                        <n-select v-model:value="formValue.pinecone.lexical_index_name"
                            placeholder="Select Lexical Index:" :options="indexOptionsLexical" />
                    </n-form-item>
                </div>
            </div>
        </div>


        <div class="form-section">
            <h3 class="section-title">Fetch Neighbor Settings</h3>

            <n-form-item label="Fetch Neighbors:" path="include_neighbors" class="form-item">
                <n-radio-group v-model:value="formValue.include_neighbors" name="radiogroup2" class="radio-group">
                    <n-space>
                        <n-radio value="yes">Yes</n-radio>
                        <n-radio value="no">No</n-radio>
                    </n-space>
                </n-radio-group>
            </n-form-item>

            <div v-if="formValue.include_neighbors == 'yes'">

                <n-form-item label="Get All Chunks" path="neighbors.get_all_neighbor_chunks"
                    class="form-item indented-field">
                    <n-select v-model:value="formValue.neighbors.get_all_neighbor_chunks" placeholder=""
                        :options="fetchAllChunksOptions" />
                </n-form-item>

                <n-form-item label="Nearest Num. of Chunks" path="neighbors.nearest_chunks_n"
                    class="form-item indented-field">
                    <n-input v-model:value="formValue.neighbors.nearest_chunks_n" placeholder="" />
                </n-form-item>

                <n-form-item label="Fetch Neighbor Pages" path="neighbors.nearest_page_or_array_members_n"
                    class="form-item indented-field">
                    <n-input v-model:value="formValue.neighbors.nearest_page_or_array_members_n" placeholder="" />
                </n-form-item>
            </div>

        </div>


        <div class="form-section">
            <h3 class="section-title">Input Data</h3>

            <n-form-item label="Select Input Mode" path="input_mode" class="form-item">
                <n-select v-model:value="formValue.input_mode" placeholder="Select Input Mode:"
                    :options="inputModeOptions" />
            </n-form-item>

            <n-form-item style="width: 100%;" v-if="formValue.input_mode == 'text'" path="data" class="form-item">
                <template #label>
                    <span class="label-with-info">
                        Input Data (JSON)
                        <InfoPopOver :content="dataFormatExample" />
                    </span>
                </template>
                <n-input v-model:value="formValue.data" placeholder="Textarea" type="textarea" class="data-textarea" />
            </n-form-item>


            <n-upload v-if="formValue.input_mode == 'file'" multiple :directory-dnd="true"
                accept=".json,application/json" @change="handleChange" ref="uploadRef" :default-upload="false" :max="5"
                class="upload-field">
                <n-upload-dragger class="upload-dragger">
                    <div style="margin-bottom: 12px">
                        <n-icon size="48" :depth="3">
                            <ArchiveIcon />
                        </n-icon>
                    </div>
                    <n-text style="font-size: 16px">
                        Click or drag a file to this area to upload
                    </n-text>
                    <n-p depth="3" style="margin: 8px 0 0 0">
                        Strictly limited to uploading following formats: ['pdf']
                    </n-p>
                </n-upload-dragger>
            </n-upload>
        </div>

        <n-form-item class="submit-row">
            <n-button :loading="isLoading" type="primary" size="large" class="submit-button" @click="submitForm">
                Submit
            </n-button>
        </n-form-item>
    </n-form>
</template>


<script setup lang="ts">
import type { FormInst, FormItemRule, FormRules, UploadFileInfo, UploadInst } from 'naive-ui'
import { computed, ref } from 'vue'
import { useUserStore } from '../../stores/user_store'
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5'
import InfoPopOver from '../../components/InfoPopOver.vue'
import { SupabaseEmbedRequestForm, SupabaseEmbedRequestText } from '../../services/vector_store/supabase_namespaces/types'
import { globalAPI } from '../../services'
import { ValidateJsonRequest, ValidateTextRequest } from '../../services/testcase/types'



const fileListLengthRef = ref(0)
const uploadRef = ref<UploadInst | null>(null)
const fileData = ref<UploadFileInfo[] | null>(null)
function handleChange(data: { fileList: UploadFileInfo[] }) {
    fileListLengthRef.value = data.fileList.length
    fileData.value = data.fileList
}


const formRef = ref<FormInst | null>(null)
const formValue = ref({
    select_vector_store: 'supabase',
    input_testcase_name: '',
    eval_model: '',
    qa_model: '',
    supabase: {
        namespace_selected: '',
        top_k: '5',
        mode: 'semantic',
        semantic_search_mode: ''
    },
    pinecone: {
        index_name_selected: '',
        top_k: '5',
        mode: 'semantic',
        lexical_index_name: ''
    },
    data: '',
    input_mode: 'text',
    include_neighbors: 'no',
    neighbors: {
        get_all_neighbor_chunks: 'no',
        nearest_chunks_n: '0',
        nearest_page_or_array_members_n: '0'
    }
})

const inputModeOptions = ['text', 'file'].map(
    v => ({
        label: v,
        value: v
    })
)
const userStore = useUserStore()
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

const llmModelOptions = computed(() => {

    let options = []
    if (userStore.userInfo?.api_keys.has_gemini_api_key) {
        options.push(
            {
                label: 'gemini-3.5-flash',
                value: 'gemini-3.5-flash',
            }
        )
        options.push(
            {
                label: 'gemini-2.5-flash',
                value: 'gemini-2.5-flash',
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


const rules: FormRules = {
    input_testcase_name: [
        {
            validator: validateTestCaseName,
            message: 'Testcase name must be inserted and be bigger than 8 characters!',
            trigger: 'input'
        }
    ],
    eval_model: [
        {
            validator: validateModel,
            message: 'Please select model!',
            trigger: 'input'
        }
    ],
    qa_model: [
        {
            validator: validateModel,
            message: 'Please select model!',
            trigger: 'input'
        }
    ],
    supabase: {
        namespace_selected: {
            validator: validateSelectSupabase,
            message: 'Please select namespace!',
            trigger: 'input'
        },
        mode: {
            validator: validateSelectSupabase,
            message: 'Please select mode!',
            trigger: 'input'
        },
        semantic_search_mode: {
            validator: validateSelectSupabase,
            message: 'Please select search mode!',
            trigger: 'input'
        },
        top_k: {
            validator: validateSelectSupabaseTopK,
            message: 'Please input number greater or equal than 1!',
            trigger: 'input'
        }
    },
    pinecone: {
        index_name_selected: {
            validator: validateSelectPinecone,
            message: 'Please select namespace!',
            trigger: 'input'
        },
        mode: {
            validator: validateSelectPinecone,
            message: 'Please select mode!',
            trigger: 'input'
        },
        lexical_index_name: {
            validator: validateSelectPinecone,
            message: 'Please select search mode!',
            trigger: 'input'
        },
        top_k: {
            validator: validateSelectPineconeTopK,
            message: 'Please input number greater or equal than 1!',
            trigger: 'input'
        }
    },
    data: {
        validator: validateData,
        message: 'Invalid text area, check info button for valid structure!',
        trigger: 'input'
    },
    neighbors: {
        nearest_chunks_n: {
            validator: validateInputNeighbor,
            message: 'Please input number greater or equal than 0!',
            trigger: 'input'
        },
        nearest_page_or_array_members_n: {
            validator: validateInputNeighbor,
            message: 'Please input number greater or equal than 0!',
            trigger: 'input'
        }
    }
}

function validateTestCaseName(rule: FormItemRule, value: string): boolean {
    return formValue.value.input_testcase_name.length >= 8
}

function validateModel(rule: FormItemRule, value: string): boolean {
    return value.length != 0
}

function validateSelectSupabase(rule: FormItemRule, value: string): boolean {
    if (formValue.value.select_vector_store == 'supabase') {
        return value.length != 0
    }
    else {
        return true
    }
}

function validateSelectSupabaseTopK(rule: FormItemRule, value: string): boolean {
    if (formValue.value.select_vector_store == 'supabase') {
        const num = Number(value);
        return !Number.isNaN(num) && num >= 1;
    }
    else {
        return true
    }
}

function validateSelectPinecone(rule: FormItemRule, value: string): boolean {
    if (formValue.value.select_vector_store == 'pinecone') {
        return value.length != 0
    }
    else {
        return true
    }
}

function validateSelectPineconeTopK(rule: FormItemRule, value: string): boolean {
    if (formValue.value.select_vector_store == 'pinecone') {
        const num = Number(value);
        return !Number.isNaN(num) && num >= 1;
    }
    else {
        return true
    }
}

function validateInputNeighbor(rule: FormItemRule, value: string): boolean {
    if (formValue.value.select_vector_store == 'pinecone') {
        const num = Number(value);
        return !Number.isNaN(num) && num >= 0;
    }
    else {
        return true
    }
}

function validateData(rule: FormItemRule, value: string): boolean {
    if (formValue.value.input_mode !== 'text') {
        return true
    }

    if (!value || value.trim() === '') {
        return false
    }

    let parsed: any
    try {
        parsed = JSON.parse(value)
    } catch (e) {
        return false
    }

    if (!Array.isArray(parsed) || parsed.length === 0) {
        return false
    }

    const allowedKeys = ['question', 'reference_answer']
    const isValidShape = parsed.every(item => {
        if (typeof item !== 'object' || item === null || Array.isArray(item)) {
            return false
        }
        const obj = item as Record<string, any>

        const hasValidQuestion = typeof obj.question === 'string'
        const hasValidReferenceAnswer =
            obj.reference_answer === undefined || typeof obj.reference_answer === 'string'
        const hasNoExtraKeys = Object.keys(obj).every(key => allowedKeys.includes(key))

        return hasValidQuestion && hasValidReferenceAnswer && hasNoExtraKeys
    })

    if (!isValidShape) {
        return false
    }

    const hasReferenceAnswerFlags = parsed.map(item => 'reference_answer' in item)
    const allHaveIt = hasReferenceAnswerFlags.every(flag => flag === true)
    const noneHaveIt = hasReferenceAnswerFlags.every(flag => flag === false)

    return allHaveIt || noneHaveIt
}

const dataFormatExample = `Array of objects, uniform shape:

Option 1 — question only:
[
  { "question": "What is the capital of France?" },
  { "question": "Name a primary color." }
]

Option 2 — question with reference_answer:
[
  { "question": "What is the capital of France?", "reference_answer": "Paris" },
  { "question": "Name a primary color.", "reference_answer": "Red" }
]`

const isLoading = ref(false)
const { mutateAsync: validateTextAPI } = globalAPI.userEval.validateText()
const { mutateAsync: validateFormAPI } = globalAPI.userEval.validateJson()


function submitForm(e: MouseEvent) {
    e.preventDefault()
    formRef.value?.validate(async (errors) => {
        if (!errors) {
            isLoading.value = true
            console.log(formValue.value)

            if (formValue.value.input_mode == 'text') {
                const data_text: ValidateTextRequest = {
                    testcase_name: formValue.value.input_testcase_name,
                    llm_model: formValue.value.eval_model,
                    eval_model: formValue.value.eval_model,
                    to_evaluate: JSON.parse(formValue.value.data),

                }
                if (formValue.value.select_vector_store == "supabase") {
                    const model = userStore.userInfo?.supabase_namespaces.filter(item => item.name == formValue.value.supabase.namespace_selected)[0].model
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

                    data_text['supabase_metadata'] = {
                        top_k: Number(formValue.value.supabase.top_k),
                        namespace: formValue.value.supabase.namespace_selected,
                        mode: formValue.value.supabase.mode,
                        semantic_search_mode: formValue.value.supabase.semantic_search_mode,
                        table_name: tableName,
                        model: model
                    }
                }

                if (formValue.value.select_vector_store == "pinecone") {
                    const model = userStore.userInfo?.pinecone_indexes.filter(item => item.name == formValue.value.pinecone.index_name_selected)[0].model
                    if (model === undefined) {
                        console.log("Undefined mode")
                        return
                    }

                    data_text['pinecone_metadata'] = {
                        top_k: Number(formValue.value.pinecone.top_k),
                        index_name: formValue.value.pinecone.index_name_selected,
                        mode: formValue.value.pinecone.mode,
                        model: model,
                        index_name_lexical: formValue.value.pinecone.mode !== 'semantic' ? formValue.value.pinecone.lexical_index_name : undefined
                    }
                }

                if (formValue.value.include_neighbors == "yes") {


                    data_text['nearest_neighbor_settings'] = {
                        nearest_chunks_n: Number(formValue.value.neighbors.nearest_chunks_n),
                        get_all_neighbor_chunks: formValue.value.neighbors.get_all_neighbor_chunks == 'yes' ? true : false,
                        nearest_page_or_array_members_n: Number(formValue.value.neighbors.nearest_page_or_array_members_n)
                    }
                }

                try {
                    const response = await validateTextAPI(data_text)
                    console.log(response)
                    alert("Data successfully evaluated")
                }
                catch (e) {
                    console.log(e)
                }
                isLoading.value = false
            }
            else if (formValue.value.input_mode == 'file') {

                if (!!fileData.value && fileData.value.length == 0) {
                    alert('Upload at least one pdf file!')
                }
                if (fileData.value && fileData.value.length > 0) {
                    const array_of_files: File[] = fileData.value
                        .map(item => item.file)
                        .filter((file): file is File => file !== undefined);


                    const data: ValidateJsonRequest = {
                        testcase_name: formValue.value.input_testcase_name,
                        llm_model: formValue.value.eval_model,
                        eval_model: formValue.value.eval_model,
                        to_evaluate: array_of_files[0],

                    }
                    if (formValue.value.select_vector_store == "supabase") {
                        const model = userStore.userInfo?.supabase_namespaces.filter(item => item.name == formValue.value.supabase.namespace_selected)[0].model
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
                            top_k: Number(formValue.value.supabase.top_k),
                            namespace: formValue.value.supabase.namespace_selected,
                            mode: formValue.value.supabase.mode,
                            semantic_search_mode: formValue.value.supabase.semantic_search_mode,
                            table_name: tableName,
                            model: model
                        }
                    }

                    if (formValue.value.select_vector_store == "pinecone") {
                        const model = userStore.userInfo?.pinecone_indexes.filter(item => item.name == formValue.value.pinecone.index_name_selected)[0].model
                        if (model === undefined) {
                            console.log("Undefined mode")
                            return
                        }

                        data['pinecone_metadata'] = {
                            top_k: Number(formValue.value.pinecone.top_k),
                            index_name: formValue.value.pinecone.index_name_selected,
                            mode: formValue.value.pinecone.mode,
                            model: model,
                            index_name_lexical: formValue.value.pinecone.mode !== 'semantic' ? formValue.value.pinecone.lexical_index_name : undefined
                        }
                    }

                    if (formValue.value.include_neighbors == "yes") {


                        data['nearest_neighbor_settings'] = {
                            nearest_chunks_n: Number(formValue.value.neighbors.nearest_chunks_n),
                            get_all_neighbor_chunks: formValue.value.neighbors.get_all_neighbor_chunks == 'yes' ? true : false,
                            nearest_page_or_array_members_n: Number(formValue.value.neighbors.nearest_page_or_array_members_n)
                        }
                    }

                    try {
                        const response = await validateFormAPI(data)
                        console.log(response)
                        alert("Data successfully evaluated")
                    }
                    catch (e) {
                        console.log(e)
                    }
                    isLoading.value = false

                }
                else {
                    isLoading.value = false
                }

            }



        }
        else {
            console.log(errors)
            console.log('Invalid')
        }
    })
}


</script>


<style scoped>
.embed-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-width: min(800px, 80%);
    margin: 0 auto;
    padding: 32px;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04);
}

.form-section {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 20px 0;
    border-bottom: 1px solid #ececec;
}

.form-section:last-of-type {
    border-bottom: none;
}

.section-title {
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #8a8a8a;
    margin: 0 0 12px 0;
}

.form-item {
    margin-bottom: 12px;
}

.form-item:last-child {
    margin-bottom: 0;
}

.indented-field {
    padding-left: 16px;
    border-left: 2px solid #eee;
    margin-left: 4px;
    align-items: stretch;
}

.radio-group {
    display: flex;
    align-items: center;
}

.inline-fields {
    display: flex;
    gap: 16px;
}

.inline-fields > .form-item {
    flex: 1;
    min-width: 0;
    max-width: 300px;
}

.half-width {
    flex: 1;
    min-width: 0;
}

.data-textarea {
    min-width: 100%;
    min-height: 280px;
    font-family: 'SFMono-Regular', Consolas, monospace;
    font-size: 13px;
}

.upload-field {
    margin-top: 4px;
}

.upload-dragger {
    border-radius: 10px;
    padding: 24px 16px;
    transition: border-color 0.15s ease, background-color 0.15s ease;
}

.upload-dragger:hover {
    border-color: #36ad6a;
    background-color: rgba(54, 173, 106, 0.04);
}

.submit-row {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
}

.submit-button {
    min-width: 140px;
    font-weight: 600;
}

.label-with-info {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
    align-items: center;
    gap: 4px;
}

@media(max-width: 900px) {
    .inline-fields {
    flex-direction: column;
}
    
}
</style>
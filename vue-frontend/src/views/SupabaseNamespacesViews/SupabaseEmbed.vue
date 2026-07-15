<template>
    <n-form class="form-class embed-form" ref="formRef" label-placement="top" :label-width="80" :model="formValue"
        :rules="rules">

        <div class="form-section">
            <h3 class="section-title">Embed into Supabase</h3>

            <n-form-item label="Select Embed Model" path="embed_model" class="form-item">
                <n-select v-model:value="formValue.embed_model" placeholder="Select Embed Model:"
                    :options="embedModelOptions" />
            </n-form-item>

            <n-form-item label="Select Namespace" path="namespace_toggle" class="form-item">
                <n-radio-group v-model:value="formValue.namespace_toggle" name="radiogroup2" class="radio-group">
                    <n-space>
                        <n-radio value="false">Use Existing</n-radio>
                        <n-radio value="true">New Namespace</n-radio>
                    </n-space>
                </n-radio-group>
            </n-form-item>

            <n-form-item v-if="formValue.namespace_toggle == 'true'" label="Input Namespace" path="namespace"
                class="form-item indented-field">
                <n-input v-model:value="formValue.namespace" placeholder="mynamespace-x" />
            </n-form-item>

            <n-form-item v-if="formValue.namespace_toggle == 'false'" label="Use Existing Namespace"
                path="namespace_selected" class="form-item indented-field">
                <n-select v-model:value="formValue.namespace_selected" placeholder="Select Namespace:"
                    :options="namespaceOptions" />
            </n-form-item>
        </div>

        <div class="form-section">
            <h3 class="section-title">Chunking</h3>

            <n-form-item label="Chunk Config" path="chunk_config_toggle" class="form-item">
                <n-radio-group v-model:value="formValue.chunk_config_toggle" name="radiogroup2" class="radio-group">
                    <n-space>
                        <n-radio value="false">No</n-radio>
                        <n-radio value="true">Yes</n-radio>
                    </n-space>
                </n-radio-group>
            </n-form-item>

            <div v-if="formValue.chunk_config_toggle == 'true'" class="inline-fields indented-field">
                <n-form-item label="Chunk Size" path="chunk_config.chunk_size" class="form-item half-width">
                    <n-input v-model:value="formValue.chunk_config.chunk_size" placeholder="0" />
                </n-form-item>

                <n-form-item label="Chunk Overlap" path="chunk_config.overlap" class="form-item half-width">
                    <n-input v-model:value="formValue.chunk_config.overlap" placeholder="0" />
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


            <n-upload v-if="formValue.input_mode == 'file'" multiple :directory-dnd="true" accept=".pdf,application/pdf"
                @change="handleChange" ref="uploadRef" :default-upload="false" :max="5" class="upload-field">
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
import type { SupabaseEmbedRequestForm, SupabaseEmbedRequestText } from '../../services/vector_store/supabase_namespaces/types'
import { globalAPI } from '../../services'



const fileListLengthRef = ref(0)
const uploadRef = ref<UploadInst | null>(null)
const fileData = ref<UploadFileInfo[] | null>(null)
function handleChange(data: { fileList: UploadFileInfo[] }) {
    fileListLengthRef.value = data.fileList.length
    fileData.value = data.fileList
}


const formRef = ref<FormInst | null>(null)
const formValue = ref({
    embed_model: '',
    input_mode: 'text',
    chunk_config_toggle: 'false',
    chunk_config: {
        chunk_size: '0',
        overlap: '0'
    },
    namespace_toggle: 'false',
    namespace_selected: '',
    namespace: '',
    data: '',
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
const embedModelOptions = computed(() => {

    let options = []
    if (userStore.userInfo?.api_keys.has_gemini_api_key) {
        options.push(
            {
                label: 'gemini-embedding-001',
                value: 'gemini-embedding-001',
            }
        )
    }
    if (userStore.userInfo?.api_keys.has_cohere_api_key) {
        options.push(
            {
                label: 'embed-v4.0',
                value: 'embed-v4.0',
            }
        )
    }
    if (userStore.userInfo?.api_keys.has_jina_api_key) {
        options.push(
            {
                label: 'jina-embeddings-v4',
                value: 'jina-embeddings-v4',
            }
        )
    }
    return options

})

const rules: FormRules = {
    namespace: [
        {
            validator: validateNamespace,
            message: 'Namespace must be at least 8 characters long!',
            trigger: 'input'
        }
    ],
    namespace_selected: [
        {
            validator: validateNamespaceSeleceted,
            message: 'Please select namespace!',
            trigger: 'input'
        }
    ],
    embed_model: [
        {
            validator: validateEmbedModel,
            message: 'Please select embed model!',
            trigger: 'input'
        }
    ],
    chunk_config: {
        chunk_size: [
            {
                validator: validateChunkConfig,
                message: 'Only numbers allowed!',
                trigger: 'input'
            },
            {
                validator: validateChunkSize,
                message: 'Chunk size bigger than 300!',
                trigger: 'input'
            }
        ],
        overlap: [
            {
                validator: validateChunkConfig,
                message: 'Only numbers allowed!',
                trigger: 'input'
            }
        ]
    },
    data: {
        validator: validateData,
        message: 'Invalid text area, check info button for valid structure!',
        trigger: 'input'
    }
}

function validateNamespace(rule: FormItemRule, value: string): boolean {
    if (formValue.value.namespace_toggle == "true") {
        return formValue.value.namespace.length >= 8
    }
    else {
        return true
    }
}

function validateNamespaceSeleceted(rule: FormItemRule, value: string): boolean {
    if (formValue.value.namespace_toggle == "false") {
        return formValue.value.namespace_selected != ''
    }
    else {
        return true
    }
}

function validateEmbedModel(rule: FormItemRule, value: string): boolean {

    return formValue.value.embed_model != ''

}

function validateChunkConfig(rule: FormItemRule, value: string): boolean {
    if (formValue.value.chunk_config_toggle == "true") {
        return /^\d*$/.test(value);
    }
    else {
        return true
    }
}

function validateChunkSize(rule: FormItemRule, value: string): boolean {
    return Number(value) >= 300;
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

    const isStringArray = parsed.every(item => typeof item === 'string')
    if (isStringArray) {
        return true
    }

    const isTextMetadataArray = parsed.every(item => {
        if (typeof item !== 'object' || item === null || Array.isArray(item)) {
            return false
        }
        const obj = item as Record<string, any>
        const hasValidText = typeof obj.text === 'string'
        const hasValidMetadata =
            typeof obj.metadata === 'object' &&
            obj.metadata !== null &&
            !Array.isArray(obj.metadata)
        return hasValidText && hasValidMetadata
    })

    return isTextMetadataArray
}

const dataFormatExample = `Option 1 — array of strings:
[
  "Time is one of the most valuable resources...",
  "Growth doesn't happen in dramatic leaps..."
]

Option 2 — array of objects with text and metadata:
[
  {
    "text": "Time is one of the most...",
    "metadata": {
      "source": "internal-docs",
      "id": "doc-alpha-001"
    }
  },
  {
    "text": "Growth doesn't happen...",
    "metadata": {
      "source": "public-blog",
      "id": "post-beta-002"
    }
  }
]`

const isLoading = ref(false)
const { mutateAsync: embedForm } = globalAPI.userSupabase.embedSupabaseRecords(true)
const { mutateAsync: embedText } = globalAPI.userSupabase.embedSupabaseRecords(false)
function submitForm(e: MouseEvent) {
    e.preventDefault()
    formRef.value?.validate(async (errors) => {
        if (!errors) {
            isLoading.value = true
            console.log(formValue.value)

            if (!!fileData.value && fileData.value.length === 0) {
                console.log('No file selected')
                alert('No file selected')

                return

            }


            if (fileData.value) { console.log(fileData.value[0]?.file) }

            if (formValue.value.input_mode == 'text') {
                const data_text: SupabaseEmbedRequestText = {
                    "namespace": formValue.value.namespace_toggle == "true" ? formValue.value.namespace : formValue.value.namespace_selected,
                    "embed_model": formValue.value.embed_model,
                    "input_mode": formValue.value.input_mode,
                    "data": formValue.value.data,
                }
                if (formValue.value.chunk_config_toggle == "true") {
                    data_text['chunk_config'] = {
                        "chunk_size": formValue.value.chunk_config.chunk_size,
                        "overlap": formValue.value.chunk_config.overlap
                    }
                }
                try {
                    const response = await embedText(data_text)
                    console.log(response)
                    alert("Data successfully emebeded")
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


                    const data: SupabaseEmbedRequestForm = {
                        "namespace": formValue.value.namespace_toggle == "true" ? formValue.value.namespace : formValue.value.namespace_selected,
                        "embed_model": formValue.value.embed_model,
                        "input_mode": formValue.value.input_mode,
                        "files": array_of_files,
                    }
                    if (formValue.value.chunk_config_toggle == "true") {
                        data['chunk_config'] = JSON.stringify({ "chunk_size": formValue.value.chunk_config.chunk_size, "overlap": formValue.value.chunk_config.overlap })
                    }
                    try {
                        const response = await embedForm(data)
                        console.log(response)
                        alert("Data successfully emebeded")
                    }
                    catch (e) {
                        console.log(e)
                    }
                    isLoading.value = false

                }
                else{
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
}

.radio-group {
    display: flex;
    align-items: center;
}

.inline-fields {
    display: flex;
    gap: 16px;
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
</style>
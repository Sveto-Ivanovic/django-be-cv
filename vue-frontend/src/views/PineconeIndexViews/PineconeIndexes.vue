<template>
    <div class="pinecone-header" v-if="!isFetching">
        <div>
            <h3>Pinecone Indexes</h3>
            <button @click="createIndex()"> Create Index <span class="arrow">{{ '+' }}</span></button>
        </div>
        <div class="seperator"></div>
    </div>


    <div class="root-div">
        <div class="pinecone-items" v-if="isSuccess && fetchedData && fetchedData?.length > 0 && !isFetching">
            <div v-for="value in fetchedData">
                <PineconeVectorStoreCard :index_name="value.index_name" :embed_model="value.embed_model"
                    :dimension="value.dimension" :vector_type="value.vector_type" :metric="value.metric"
                    :route-to="'Dashboard'"></PineconeVectorStoreCard>
            </div>

        </div>
        <div class="no-index" v-else-if="isSuccess && fetchedData && fetchedData?.length == 0 && !isFetching"> No
            Pinecone
            Indexes found </div>
        <div class="loader" v-else-if="isFetching">
            <LoadingComponent></LoadingComponent>
        </div>
        <div class="error-event" v-else-if="isFetched && isError && !!fetchedData"> Error occured ...</div>

    </div>

    <n-modal v-model:show="showModal">
        <n-card style="width: 600px" title="" :bordered="false" size="huge" role="dialog" class="index-modal-card">

            <n-form class="form-class" ref="formRef" :label-width="80" :model="formValue" :rules="rules">

                <n-form-item label="Index Name" path="index_name" class="form-item-full">
                    <n-input v-model:value="formValue.index_name" placeholder="Input Index Name" class="index-input" />
                </n-form-item>

                <n-form-item label="Index Type" path="index_type" class="form-item-full">
                    <n-radio-group v-model:value="formValue.index_type" name="radiogroup2" class="radio-group-row">
                        <n-space>
                            <n-radio value="dense">Dense Vector</n-radio>
                            <n-radio value="textsearch">Text Search</n-radio>
                        </n-space>
                    </n-radio-group>
                </n-form-item>

                <n-form-item v-if="formValue.index_type == 'dense'" label="Select Vector Size" path="vector_size"
                    class="form-item-full">
                    <n-radio-group v-model:value="formValue.vector_size" name="radiogroup1" class="radio-group-row">
                        <n-space>
                            <n-radio value="2048">2048</n-radio>
                            <n-radio value="3072">3072</n-radio>
                            <n-radio value="1536">1536</n-radio>
                        </n-space>
                    </n-radio-group>
                </n-form-item>


                <n-form-item class="submit-item">
                    <n-button @click="handleSubmit" type="primary" class="submit-btn" :loading="isDisabled">
                        Submit
                    </n-button>
                </n-form-item>

            </n-form>
        </n-card>
    </n-modal>
</template>


<script setup lang="ts">
import { computed, ref } from 'vue';
import { globalAPI } from '../../services';
import PineconeVectorStoreCard from '../../components/VectorStoreCards/PineconeVectorStoreCard.vue';
import { useRouter } from 'vue-router';
import LoadingComponent from '../../components/LoadingComponent.vue';
import type { FormInst, FormItemRule, FormRules } from 'naive-ui'

const { isFetching, isFetched, isSuccess, isError, data } = globalAPI.userPinecone.fetchPineconeIndexes()
const fetchedData = computed(() => {
    console.log(data.value?.data.response)
    if (data.value?.data.response && typeof data.value?.data.response === 'object') { return data.value?.data.response ?? [] }
})
const router = useRouter()
const showModal = ref(false)
const formRef = ref<FormInst | null>(null)

const formValue = ref({
    index_name: '',
    vector_size: "3072",
    index_type: 'dense'

})


const rules: FormRules = {
    index_name: [{
        required: true,
        message: 'Please input your index name',
        trigger: 'blur'
    },
    {
        validator: validateIndexName,
        message: "Index name can only contain characters, numbers and '-'!",
        trigger: 'input'
    },

    ]
}

function validateIndexName(rule: FormItemRule, value: string): boolean {
    return /^[A-Za-z0-9-]+$/.test(formValue.value.index_name);
}
function createIndex() {
    showModal.value = true
}

const { mutateAsync: createIndexAPI } = globalAPI.userPinecone.createPineconeIndex()
const { mutateAsync: createIndexTextsearchAPI } = globalAPI.userPinecone.createPineconeIndexTextsearch()
const isDisabled = ref(false)

function handleSubmit(e: MouseEvent) {
    e.preventDefault()
    isDisabled.value = true
    formRef.value?.validate(async (errors) => {
        if (!errors) {
            if (formValue.value.index_type == 'dense') {
                const response = await createIndexAPI({
                    'index_name': formValue.value.index_name as string,
                    'vector_size': formValue.value.vector_size,
                    'type_of_index': 'dense'
                })
                isDisabled.value = false
                showModal.value = false
            }
            else if (formValue.value.index_type == 'textsearch') {
                const response = await createIndexTextsearchAPI({
                    'index_name': formValue.value.index_name as string
                })
                isDisabled.value = false
                showModal.value = false
            }
        }
        else {
            console.log(errors)
            isDisabled.value = false
            console.log('Invalid')
        }
    })
}

</script>


<style scoped>
.index-modal-card {
    border-radius: 12px;
}

.form-class {
    display: flex;
    flex-direction: column;
    padding: 24px;
    width: 80%;
    gap: 24px;
}

.form-item-full {
    width: 100%;
}

.form-item-full :deep(.n-form-item-label) {
    font-weight: 600;
    font-size: 14px;
}

.index-input {
    width: 100%;
}

.radio-group-row {
    display: flex;
    align-items: center;
}

.submit-item {
    display: flex;
    justify-content: center;
    margin-top: 12px;
}

.submit-item :deep(.n-form-item-blank) {
    justify-content: center;
}

.submit-btn {
    min-width: 140px;
}

.loader {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.root-div {
    height: 100vh;

}

.pinecone-header {
    padding-bottom: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 32px;

}

.pinecone-header h3 {
    font-size: clamp(16px, 3vh, 28px);
}

.pinecone-header button {
    color: var(--text-color);
    font-size: 16px;
    border: none;
    font-weight: 500;
    background-color: transparent;
    cursor: pointer;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    gap: 8px;
}

.arrow {
    font-size: 20px;
    font-weight: 600;
}

.pinecone-header button:hover {
    color: gray;
}

.pinecone-header div {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    width: 90%;
    align-items: center;

}

.seperator {
    height: 0px;
    border: 1px solid;
    width: 100%;
}

.no-index {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding-top: 32px;
    font-weight: 600;
    font-size: 24px;
    color: var(--text-color);
    font-family: 'Times New Roman', Times, serif;
    letter-spacing: 0.01em;
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

.pinecone-items {
    display: flex;
    flex-direction: row;
    gap: 16px;
    width: 100%;
    justify-content: space-around;
    flex-wrap: wrap;
}

@media (max-width: 900px) {
    .pinecone-items {
        display: flex;
        flex-direction: column;
        gap: 16px;
        justify-content: center;
        align-items: center;
    }

    .pinecone-header {
        padding-bottom: 50px;
    }
}
</style>
<template>

    <div class="supabase-header" v-if="!isFetching">
        <div>
            <h3>Supabase Records for Namespace: {{ $route.params.namespace }}</h3>
            <button @click="deleteNamespace()" class="delete-table"
                :class="{ 'disable-button-class': fetchedData?.length == 0 || hasBeenClicked }"> Delete Namespace</button>
        </div>

        <div class="seperator"></div>
    </div>


    <div class="root-div">
        <div class="controls" v-if="isSuccess && fetchedData && fetchedData.length > 0 && !isFetching">
            <input v-model="searchQuery" type="text" placeholder="Search records..." class="search-input" />
        </div>
        <div class="supabase-table" v-if="isSuccess && fetchedData && fetchedData?.length > 0 && !isFetching">
            <n-data-table :single-line="false" :columns="columns" :data="filteredData" :pagination="pagination"
                :bordered="true" :scroll-x="tableScrollX" />
        </div>
        <div class="no-namespace" v-else-if="isSuccess && fetchedData && fetchedData?.length == 0 && !isFetching">
            <n-data-table :columns="columns" :data="fetchedData" :pagination="pagination" :bordered="true" />
        </div>
        <div class="loader" v-else-if="isFetching">
            <LoadingComponent></LoadingComponent>
        </div>
        <div class="error-event" v-else-if="isFetched && isError && !!fetchedData"> Error occured ...</div>
    </div>


</template>


<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { globalAPI } from '../../services';
import { computed, h, ref } from 'vue';
import LoadingComponent from '../../components/LoadingComponent.vue';
import { NButton, type DataTableColumns } from 'naive-ui'
import { useWindowSize } from '@vueuse/core';


const route = useRoute()

const { data, isError, isFetched, isFetching, isSuccess } = globalAPI.userSupabase.fetchSupabaseNamespaceRecords({
    namespace: route.params.namespace as string,
    table_name: route.params.table_name as string
})

const fetchedData = computed(() => {
    const q = searchQuery.value.toLowerCase()
    if (data.value?.data.response && typeof data.value?.data.response === 'object') {

        const updated_data = data.value.data.response.records.map(record => ({
            namespace: record.namespace,
            source: record.source,
            chunk_number: record.chunk_number,
            id: record.id,
            content: record.content,
            model: record.model,
            is_chunk: record.is_chunk,
            type: record.type,
            metadata: record.metadata,
            created_at: record.created_at
        })) ?? []

        return updated_data
    }
    return []
})

const normalize = (value: string) =>
    String(value)
        .toLowerCase()
        .replace(/\s+/g, ' ')
        .trim()
const excludeIds = ref<string[]>([])
const searchQuery = ref('')
const filteredData = computed(() => {

    const notExcluded = fetchedData.value.filter(
        record => !excludeIds.value.includes(String(record.id))
    )

    if (!searchQuery.value.trim()) return notExcluded

    const q = searchQuery.value.toLowerCase().trim()

    const filteredVal = notExcluded.filter(record =>
        normalize(record.id).toLowerCase().includes(q) ||
        normalize(record.namespace).toLowerCase().includes(q) ||
        normalize(record.source).toLowerCase().includes(q) ||
        normalize(record.content).toLowerCase().includes(q) ||
        normalize(record.model).toLowerCase().includes(q) ||
        normalize(record.type).toLowerCase().includes(q)
    )


    return filteredVal
})

type SupabaseNamespaceRecordUpdated = {
    id: string,
    namespace: string;
    source: string;
    chunk_number: number;
    content: string;
    model: string;
    is_chunk: boolean;
    type: string;
    metadata: Record<string, any>
    created_at: string
}


function createColumns(

    {
        deleteRow
    }: {
        deleteRow: (row: SupabaseNamespaceRecordUpdated) => void
    }
): DataTableColumns<SupabaseNamespaceRecordUpdated> {
    return [
        { title: 'ID', key: 'id', width: 120, sorter: 'default' },
        { title: 'Namespace', key: 'namespace', width: 120, sorter: 'default' },
        { title: 'Source', key: 'source', width: 120, sorter: 'default' },
        { title: 'Chunk_number', key: 'chunk_number', width: 100, sorter: 'default' },
        {
            title: 'Content',
            key: 'content',
            width: 200,
            ellipsis: {
                tooltip: {
                    contentStyle: {
                        maxWidth: '400px',
                        maxHeight: '200px',
                        overflow: 'auto',
                        wordBreak: 'break-word',
                        whiteSpace: 'pre-wrap'
                    },
                }
            }
        },
        {
            title: 'Metadata',
            key: 'metadata',
            width: 200,
            ellipsis: {
                tooltip: {
                    contentStyle: {
                        maxWidth: '400px',
                        maxHeight: '300px',
                        overflow: 'auto',
                        wordBreak: 'break-word',
                        whiteSpace: 'pre-wrap'
                    }
                } as any
            },
            render(row) {
               return JSON.stringify(row.metadata, null, 2)
            }
        },
        { title: 'Model', key: 'model', width: 100, sorter: 'default' },
        { title: 'Is Chunk', key: 'is_chunk', width: 90, sorter: 'default' },
        { title: 'Type', key: 'type', width: 100, sorter: 'default' },
        {
            title: 'Created At',
            key: 'created_at',
            width: 180,
            sorter: (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
            render(row) {
                const date = new Date(row.created_at)
                return date.toLocaleString(undefined, {
                    year: 'numeric',
                    month: 'short',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                })
            }
        },
        {
            title: 'Delete Row',
            key: 'delete_row',
            width: 250,
            render(row) {
                return h(
                    NButton,
                    {
                        strong: true,
                        size: 'small',
                        color: 'red',
                        onClick: () => deleteRow(row)
                    },
                    { default: () => 'Delete Row' }
                )
            }
        }

    ]
}

const { width, height } = useWindowSize()
const { mutateAsync: deleteRecord } = globalAPI.userSupabase.deleteRecord()
const columns = createColumns(
    {
        deleteRow(row: SupabaseNamespaceRecordUpdated) {
            excludeIds.value.push(row.id as string)
            const response = deleteRecord({
                namespace: route.params.namespace as string,
                table_name: route.params.table_name as string,    
                ids: [row.id as string]
            
            })
              console.log(response)
        }
    }
)
const tableScrollX = computed(() =>
    columns.reduce((sum, col: any) => sum + (col.width ?? 100), 0)
)
const pagination = {
    pageSize: 5
}
const { mutateAsync: deleteNamespaceAPI } = globalAPI.userSupabase.deleteNamespace()
const hasBeenClicked = ref(false)
const router = useRouter()

async function deleteNamespace() {
    hasBeenClicked.value = true
    const response = await deleteNamespaceAPI({
        namespace: route.params.namespace as string,
        table_name: route.params.table_name as string,
    })
  
    router.push({
        name: 'SupabaseNameSpaces'
    })
}
</script>


<style scoped>
.delete-table {
    padding: 10px 18px;
    border: none;
    border-radius: 6px;
    background-color: #dc3545;
    color: #fff;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease, opacity 0.2s ease;
}

.delete-table:hover {
    background-color: #c82333;
}


.disable-button-class {
    background-color: #bdbdbd;
    color: #666;
    cursor: not-allowed;
    opacity: 0.7;
    pointer-events: none;
}

.controls {
    display: flex;
    justify-content: center;
    padding: 16px;
}

.search-input {
    width: 100%;
    max-width: 400px;
    padding: 8px 12px;
    border-radius: 6px;
    border: 1px solid #ccc;
    font-size: 14px;
}

.loader {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.root-div {
     min-height: 100%;
}

.supabase-header {
    padding-bottom: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 32px;

}

.supabase-header h3 {
    font-size: clamp(16px, 3vh, 28px);
}


.supabase-header div {
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

.no-namespace {
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
</style>
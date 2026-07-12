<template>

    <div class="testcase-header" v-if="!isFetching">
        <div>
            <h3>Testcase Records for: {{ fetchedData[0].test_case_name ?? 'Unknown' }}</h3>
            <button @click="deleteAggregate()" class="delete-table"
                :class="{ 'disable-button-class': fetchedData?.length == 0 || hasBeenClicked }"> Delete
                Testcase</button>
        </div>

        <div class="seperator"></div>
    </div>


    <div class="root-div">

        <div class="testcase-table" v-if="isSuccess && fetchedData && fetchedData?.length > 0 && !isFetching">
            <div class="graphs">

                <div class="metric-and-bar">
                    <div class="metric-card-wrapper"
                        v-if="formated_data.aggregate?.answer_correctness && formated_data.aggregate?.answer_relevancy && formated_data.aggregate?.context_recall && formated_data.aggregate?.faithfulness">
                        <EvalCard :num-of-tests="formated_data.xdata.length"
                            :answer-correctness="formated_data.aggregate?.answer_correctness"
                            :answer-relevancy="formated_data.aggregate?.answer_relevancy"
                            :context-recall="formated_data.aggregate?.context_recall"
                            :faithfulness="formated_data.aggregate?.faithfulness">
                        </EvalCard>

                    </div>
                    <div class="bar-chart-wrapper">
                        <VueApexCharts type="bar" height="400" :options="getOptionsBar" :series="getSeries">
                        </VueApexCharts>
                    </div>
                </div>
            </div>
            <div class="controls">
                <input v-model="searchQuery" type="text" placeholder="Search records..." class="search-input" />
            </div>
            <div class="table-wrapper">
                <div style="width: 80%;">
                    <n-data-table :single-line="false" :columns="columns" :data="filteredData" :pagination="pagination"
                        :bordered="true" :scroll-x="tableScrollX" />

                </div>
            </div>



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
import { TestCaseListItem } from '../../services/testcase/types';
import VueApexCharts from 'vue3-apexcharts'
import { get_options_bar, get_series_bar } from './helper_functions/statistic_graphs';
import EvalCard from '../../components/EvalCard.vue';


const route = useRoute()

const { data, isError, isFetched, isFetching, isSuccess } = globalAPI.userEval.getTestCaseEvals({
    aggregate_id: route.params.id as string,
})

const fetchedData = computed(() => {

    if (data.value?.data.response && typeof data.value?.data.response === 'object') {

        const updated_data: TestCaseListItem[] = data.value.data.response.map(record => ({
            id: record.id,
            aggregate_id: record.aggregate_id,
            test_case_name: record.test_case_name ?? null,
            qa_model_used: record.qa_model_used ?? null,
            validation_model_used: record.validation_model_used ?? null,
            aggregate_metadata: record.aggregate_metadata ?? null,
            created_at: record.created_at,

            user_input: record.user_input ?? null,
            retrieved_context_text: record.retrieved_context_text ?? null,
            retrieved_context_array: record.retrieved_context_array ?? null,
            response: record.response ?? null,
            reference: record.reference ?? null,

            faithfulness: record.faithfulness ?? null,
            faithfulness_explanation: record.faithfulness_explanation ?? null,
            answer_relevancy: record.answer_relevancy ?? null,
            answer_relevancy_explanation: record.answer_relevancy_explanation ?? null,
            answer_correctness: record.answer_correctness ?? null,
            answer_correctness_explanation: record.answer_correctness_explanation ?? null,
            context_recall: record.context_recall ?? null,
            context_recall_explanation: record.context_recall_explanation ?? null,
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
        record => !excludeIds.value.includes(String(record.aggregate_id))
    )

    if (!searchQuery.value.trim()) return notExcluded

    const q = searchQuery.value.toLowerCase().trim()

    const filteredVal = notExcluded.filter(record =>
        normalize(record.id).toLowerCase().includes(q) ||
        normalize(record.aggregate_id).toLowerCase().includes(q) ||
        normalize(record.answer_correctness_explanation ?? '').toLowerCase().includes(q) ||
        normalize(record.answer_relevancy_explanation ?? '').toLowerCase().includes(q) ||
        normalize(record.context_recall_explanation ?? '').toLowerCase().includes(q) ||
        normalize(record.faithfulness_explanation ?? '').toLowerCase().includes(q) ||
        normalize(record.qa_model_used ?? '').toLowerCase().includes(q) ||
        normalize(record.reference ?? '').toLowerCase().includes(q) ||
        normalize(record.response ?? '').toLowerCase().includes(q) ||
        normalize(record.retrieved_context_text ?? '').toLowerCase().includes(q) ||
        normalize(record.test_case_name ?? '').toLowerCase().includes(q) ||
        normalize(record.user_input ?? '').toLowerCase().includes(q) ||
        normalize(record.validation_model_used ?? '').toLowerCase().includes(q)
    )


    return filteredVal
})




function createColumns(): DataTableColumns<TestCaseListItem> {
    return [
        { title: 'ID', key: 'id', width: 120, sorter: 'default' },
        { title: 'Aggregate ID', key: 'aggregate_id', width: 120, sorter: 'default' },
        { title: 'TestCase Name', key: 'test_case_name', width: 120, sorter: 'default' },
        {
            title: 'User Question', key: 'user_input', sorter: 'default', width: 200,
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
            title: 'AI Response', key: 'response', sorter: 'default', width: 200,
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
        { title: 'QA Model', key: 'qa_model_used', width: 100, sorter: 'default' },
        { title: 'Eval Model', key: 'validation_model_used', width: 100, sorter: 'default' },
        {
            title: 'Retrieved Context', key: 'retrieved_context_text', sorter: 'default', width: 200,
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
            title: 'Reference Answer', key: 'reference', sorter: 'default', width: 200,
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
            title: 'Retrieved Context (Array)',
            key: 'retrieved_context_array',
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
                return JSON.stringify(row.retrieved_context_array, null, 4)
            }
        },
        { title: 'Faithfulness', key: 'faithfulness', width: 100, sorter: 'default' },
        {
            title: 'Faithfulness Explanation', key: 'faithfulness_explanation', sorter: 'default', width: 200,
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
        { title: 'Answer Relevancy', key: 'answer_relevancy', width: 100, sorter: 'default' },
        {
            title: 'Answer Relevancy Explanation', key: 'answer_relevancy_explanation', sorter: 'default', width: 200,
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
        { title: 'Answer Correctness', key: 'answer_correctness', width: 100, sorter: 'default' },
        {
            title: 'Answer Correctness Explanation', key: 'answer_correctness_explanation', sorter: 'default', width: 200,
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
        { title: 'Context Recall', key: 'context_recall', width: 100, sorter: 'default' },
        {
            title: 'Context Recall Explanation', key: 'context_recall_explanation', sorter: 'default', width: 200,
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
        }

    ]
}


const columns = createColumns()
const tableScrollX = computed(() =>
    columns.reduce((sum, col: any) => sum + (col.width ?? 100), 0)
)
const pagination = {
    pageSize: 5
}
const { mutateAsync: deleteAggregateAPI } = globalAPI.userEval.deleteAggregate()
const hasBeenClicked = ref(false)
const router = useRouter()

async function deleteAggregate() {
    hasBeenClicked.value = true
    const response = await deleteAggregateAPI({
        aggregate_id: route.params.id as string,
    })

    router.push({
        name: 'TestCaseResults'
    })
}



//// logic  for diagrams 

export type FormatedData = {
    xdata: string[];
    xdate: string[];
    qa_models: string[];
    val_models: string[];
    aggregate: {
        answer_relevancy: {
            min: number | null;
            max: number | null;
            avg: number | null;
        } | null
        answer_correctness: {
            min: number | null;
            max: number | null;
            avg: number | null;
        } | null
        context_recall: {
            min: number | null;
            max: number | null;
            avg: number | null;
        } | null
        faithfulness: {
            min: number | null;
            max: number | null;
            avg: number | null;
        } | null
    } | null;
    answer_relevancy: number[];
    answer_correctness: number[];
    context_recall: number[];
    faithfulness: number[];
    answer_relevancy_categories: string[];
    answer_correctness_categories: string[];
    context_recall_categories: string[];
    faithfulness_categories: string[];
}

const formated_data = computed<FormatedData>(() => {
    if (data.value?.data.response && Array.isArray(data.value.data.response)) {

        const response = [...data.value.data.response].sort(
            (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        )

        const xdata = response.map((item) => {
            if (item.test_case_name)
                return item.test_case_name
            else
                return 'unknown'
        }
        )
        const xdate = response.map((item) => new Date(item.created_at).toLocaleDateString())
        const qa_models = response.map((item) => {
            if (item.qa_model_used)
                return item.qa_model_used
            else
                return 'unknown'
        })
        const val_models = response.map((item) => {
            if (item.validation_model_used)
                return item.validation_model_used
            else
                return 'unknown'
        })




        const answer_relevancy = response.map((item) =>
            item.answer_relevancy ?? 0
        )

        const answer_correctness = response.map((item) =>
            item.answer_correctness ?? 0
        )
        0
        const context_recall = response.map((item) =>
            item.context_recall ?? 0
        )

        const faithfulness = response.map((item) =>
            item.faithfulness ?? 0
        )

        const getCategory = (x: number): string => {
            if (x < 0.25) return "<0.25"
            if (x < 0.5) return "0.25-0.5"
            if (x < 0.7) return "0.5-0.7"
            if (x < 0.8) return "0.7-0.8"
            if (x < 0.9) return "0.8-0.9"
            return ">0.9"
        }

        const answer_relevancy_categories = response.map((item) =>
            getCategory(item.answer_relevancy ?? 0)
        )

        const answer_correctness_categories = response.map((item) =>
            getCategory(item.answer_correctness ?? 0)
        )

        const context_recall_categories = response.map((item) =>
            getCategory(item.context_recall ?? 0)
        )

        const faithfulness_categories = response.map((item) =>
            getCategory(item.faithfulness ?? 0)
        )

        const aggregate = {
            answer_relevancy: {
                min: Math.min(...answer_relevancy),
                max: Math.max(...answer_relevancy),
                avg: answer_relevancy.reduce((sum, value) => sum + value, 0) / answer_relevancy.length
            },
            answer_correctness: {
                min: Math.min(...answer_correctness),
                max: Math.max(...answer_correctness),
                avg: answer_correctness.reduce((sum, value) => sum + value, 0) / answer_correctness.length
            },
            context_recall: {
                min: Math.min(...context_recall),
                max: Math.max(...context_recall),
                avg: context_recall.reduce((sum, value) => sum + value, 0) / context_recall.length
            },
            faithfulness: {
                min: Math.min(...faithfulness),
                max: Math.max(...faithfulness),
                avg: faithfulness.reduce((sum, value) => sum + value, 0) / faithfulness.length
            }
        }


        return {
            xdata,
            xdate,
            qa_models,
            val_models,
            aggregate,
            answer_relevancy,
            answer_correctness,
            context_recall,
            faithfulness,
            answer_correctness_categories,
            answer_relevancy_categories,
            context_recall_categories,
            faithfulness_categories
        }
    } else {
        return {
            xdata: [],
            xdate: [],
            qa_models: [],
            val_models: [],
            aggregate: null,
            answer_relevancy: [],
            answer_correctness: [],
            context_recall: [],
            faithfulness: [],
            answer_correctness_categories: [],
            answer_relevancy_categories: [],
            context_recall_categories: [],
            faithfulness_categories: []
        }
    }
})



const getOptionsBar = get_options_bar(formated_data.value)
const getSeries = get_series_bar(formated_data)


</script>


<style scoped>
.root-div {
    width: 100%;
}

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

.table-wrapper {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

}

.testcase-table {
    width: 100%;
}

.testcase-header {
    padding-bottom: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 32px;

}

.testcase-header h3 {
    font-size: clamp(16px, 3vh, 28px);
}


.testcase-header div {
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

.graphs {
    padding-bottom: 128px;
}

.metric-and-bar {
    width: 100%;
    display: flex;
    flex-direction: row;
    padding-top: 64px;
}

.metric-card-wrapper {
    width: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.bar-chart-wrapper {
    width: 45%;
}

@media (max-width: 900px) {

.metric-and-bar {
    width: 100%;
    display: flex;
    flex-direction: column;
    padding-top: 64px;
}

.metric-card-wrapper {
    width: 90%;
}

.bar-chart-wrapper {
    width: 90%;
}
}
</style>
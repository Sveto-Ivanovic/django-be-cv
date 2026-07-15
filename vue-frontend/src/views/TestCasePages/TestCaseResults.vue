<template>
    <div>
        <div class="testcase-header" v-if="!isFetching">
            <div>
                <h3>Testcases:</h3>
                <button @click="EvaluateRAG"> Create Index <span class="arrow">{{ '>' }}</span></button>
            </div>
            <div class="seperator"></div>
        </div>

        <div class="root-div">
            <div class="testcase-items" v-if="isSuccess && fetchedData && fetchedData?.length > 0 && !isFetching">
                <div v-for="value in fetchedData">


                    <TestCaseCard :id="value.id" :aggregate_metadata="value.aggregate_metadata"
                        :created_at="value.created_at" :number_of_testcases="value.number_of_testcases"
                        :validation_model_used="value.validation_model_used" :qa_model_used="value.qa_model_used"
                        :test_case_name="value.test_case_name"></TestCaseCard>


                </div>

            </div>
            <div class="no-namespace" v-else-if="isSuccess && fetchedData && fetchedData?.length == 0 && !isFetching">
                No
                No testcases found ... </div>
            <div class="loader" v-else-if="isFetching">
                <LoadingComponent></LoadingComponent>
            </div>
            <div class="error-event" v-else-if="isFetched && isError && !!fetchedData"> Error occured ...</div>
        </div>

        <div class="graph" v-if="isSuccess && fetchedData && fetchedData?.length > 0 && !isFetching">
            <div class="header-wrapper">
                <div class="hist-header">
                    <h3>Testcase History:</h3>
                </div>
                <div class="seperator"></div>
            </div>
            <div class="graph-wrapper">
                <VueApexCharts type="line" :height="height_line" :width="width_line" :options="options_line"
                    :series="series_line">

                </VueApexCharts>
            </div>
        </div>
    </div>
</template>


<script setup lang="ts">
import { computed, ref } from 'vue';
import { globalAPI } from '../../services'
import LoadingComponent from '../../components/LoadingComponent.vue';
import TestCaseCard from '../../components/TestCaseCard.vue';
import { useRouter } from 'vue-router';
import VueApexCharts from 'vue3-apexcharts'
import type { ApexOptions } from 'apexcharts'
import { useWindowSize } from '@vueuse/core'

const { isFetching, isFetched, isSuccess, isError, data } = globalAPI.userEval.getAggregateResults()

const fetchedData = computed(() => {
    console.log(data.value?.data.response)
    if (data.value?.data.response && typeof data.value?.data.response === 'object') { return data.value?.data.response ?? [] }
})

const router = useRouter()
function EvaluateRAG() {
    router.push({
        name: "TestCaseCreate"
    })
}

type FormattedData = {
    xdata: string[]
    xdate: string[]
    qa_models: string[]
    val_models: string[]
    number_of_tests: number[]
    answer_relevancy: number[]
    answer_correctness: number[]
    context_recall: number[]
    faithfulness: number[]
    series_answer_relevancy: {
        x: string;
        y: number;
        qa_model: string;
        eval_model: string;
        date: string;
        num_test: number;
    }[]
    series_answer_correctness: {
        x: string;
        y: number;
        qa_model: string;
        eval_model: string;
        date: string;
        num_test: number;
    }[]
    series_answer_context_recall: {
        x: string;
        y: number;
        qa_model: string;
        eval_model: string;
        date: string;
        num_test: number;
    }[]
    series_answer_faithfulness: {
        x: string;
        y: number;
        qa_model: string;
        eval_model: string;
        date: string;
        num_test: number;
    }[]
}

const formated_data = computed<FormattedData>(() => {
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
        const number_of_tests = response.map((item) => {
            if (item.number_of_testcases)
                return item.number_of_testcases
            else
                return 0
        })

        const answer_relevancy = response.map((item) =>
            item.aggregate_metadata?.answer_relevancy ?? 0
        )

        const answer_correctness = response.map((item) =>
            item.aggregate_metadata?.answer_correctness ?? 0
        )

        const context_recall = response.map((item) =>
            item.aggregate_metadata?.context_recall ?? 0
        )

        const faithfulness = response.map((item) =>
            item.aggregate_metadata?.faithfulness ?? 0
        )

        const round2 = (value?: number): number =>
            Math.round((value ?? 0) * 100) / 100;

        const series_answer_relevancy = response.map((item) => ({
            x: item.test_case_name ?? "Unknown",
            y: round2(item.aggregate_metadata?.answer_relevancy),
            qa_model: item.qa_model_used ?? "Unknown",
            eval_model: item.validation_model_used ?? "Unknown",
            date: new Date(item.created_at).toLocaleDateString(),
            num_test: item.number_of_testcases ?? 0,
        }));

        const series_answer_correctness = response.map((item) => ({
            x: item.test_case_name ?? "Unknown",
            y: round2(item.aggregate_metadata?.answer_correctness),
            qa_model: item.qa_model_used ?? "Unknown",
            eval_model: item.validation_model_used ?? "Unknown",
            date: new Date(item.created_at).toLocaleDateString(),
            num_test: item.number_of_testcases ?? 0,
        }));

        const series_answer_context_recall = response.map((item) => ({
            x: item.test_case_name ?? "Unknown",
            y: round2(item.aggregate_metadata?.context_recall),
            qa_model: item.qa_model_used ?? "Unknown",
            eval_model: item.validation_model_used ?? "Unknown",
            date: new Date(item.created_at).toLocaleDateString(),
            num_test: item.number_of_testcases ?? 0,
        }));

        const series_answer_faithfulness = response.map((item) => ({
            x: item.test_case_name ?? "Unknown",
            y: round2(item.aggregate_metadata?.faithfulness),
            qa_model: item.qa_model_used ?? "Unknown",
            eval_model: item.validation_model_used ?? "Unknown",
            date: new Date(item.created_at).toLocaleDateString(),
            num_test: item.number_of_testcases ?? 0,
        }));
        return {
            xdata,
            xdate,
            qa_models,
            val_models,
            number_of_tests,
            answer_relevancy,
            answer_correctness,
            context_recall,
            faithfulness,
            series_answer_relevancy,
            series_answer_correctness,
            series_answer_context_recall,
            series_answer_faithfulness
        }
    } else {
        return {
            xdata: [],
            xdate: [],
            qa_models: [],
            val_models: [],
            number_of_tests: [],
            answer_relevancy: [],
            answer_correctness: [],
            context_recall: [],
            faithfulness: [],
            series_answer_relevancy: [],
            series_answer_correctness: [],
            series_answer_context_recall: [],
            series_answer_faithfulness: []

        }
    }
})
const options_line = computed<ApexOptions>(() => ({
    chart: {
        type: 'line',
        zoom: { enabled: false },
        toolbar: { show: true, tools: { download: true } }
    },
    dataLabels: { enabled: false },
    stroke: { width: [5, 5, 5, 5], curve: 'straight', dashArray: [0, 0, 0, 0] },
    title: { text: 'Evaluation Progress', align: 'left' },
    markers: { size: 4, hover: { sizeOffset: 6 } },
    xaxis: { categories: formated_data.value.xdata },
    tooltip: {
        intersect: false,
        shared: true,

        custom: function ({ series, seriesIndex, dataPointIndex, w }) {
            const data = w.globals.initialSeries[seriesIndex].data[dataPointIndex];
            const data_y = w.globals.initialSeries
            const seriesConfig = w.config.series as { name: string }[]
            const metricName = seriesConfig
            const color = w.globals.colors

            return `
            <div class="custom-tooltip">
                <div class="tooltip-header">
                   
                    <span class="test-name">${data.x}</span>
                </div>
                <div class="tooltip-metric">
                     <span class="dot" style="background:${color[0]}"></span>
                    <span class="metric-label">${metricName[0]?.name}</span>
                    <span class="metric-value">${data_y[0].data[dataPointIndex].y}</span>
                </div>
                <div class="tooltip-metric">
                    <span class="dot" style="background:${color[1]}"></span>
                    <span class="metric-label">${metricName[1]?.name}</span>
                    <span class="metric-value">${data_y[1].data[dataPointIndex].y}</span>
                </div>
                <div class="tooltip-metric">
                    <span class="dot" style="background:${color[2]}"></span>
                    <span class="metric-label">${metricName[2]?.name}</span>
                    <span class="metric-value">${data_y[2].data[dataPointIndex].y}</span>
                </div>
                <div class="tooltip-metric">
                    <span class="dot" style="background:${color[3]}"></span>
                    <span class="metric-label">${metricName[3]?.name}</span>
                    <span class="metric-value">${data_y[3].data[dataPointIndex].y}</span>
                </div>
                <div class="tooltip-body">
                    <div class="row"><span class="label">QA Model</span><span class="value">${data.qa_model}</span></div>
                    <div class="row"><span class="label">Eval Model</span><span class="value">${data.eval_model}</span></div>
                    <div class="row"><span class="label">Date</span><span class="value">${data.date}</span></div>
                    <div class="row"><span class="label">Tests Run</span><span class="value">${data.num_test}</span></div>
                </div>
            </div>
        `


        }
    },
    grid: { borderColor: '#f1f1f1', padding: { left: 20, right: 20, top: 0, bottom: 0 } },
}));

const series_line = computed(() => [
    { name: 'Answer Relevancy', data: formated_data.value.series_answer_relevancy },
    { name: 'Answer Correctness', data: formated_data.value.series_answer_correctness },
    { name: 'Context Recall', data: formated_data.value.series_answer_context_recall },
    { name: 'Faithfulness', data: formated_data.value.series_answer_faithfulness },
]);

const { width, height } = useWindowSize()

let height_line = computed(() => {
    if (width.value <= 768) {
        return 300;
    }
    else if (width.value <= 1200) {
        return 400;
    }
    else {
        return 450;
    }
})
let width_line = computed(() => {

    if (width.value <= 768) {
        return 300;
    }
    else if (width.value <= 1200) {
        return 500;
    }
    else {
        return 800;
    }
})

</script>


<style scoped>
.loader {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}



.graph {
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 16px;

}

.header-wrapper {
    width: 90%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 16px;
}

.hist-header {
    width: 100%;

}

.hist-header h3 {
    font-size: clamp(16px, 3vh, 28px);
}

.graph-wrapper {
    padding-top: 64px;
}

.testcase-header {
    padding-bottom: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

}

.testcase-header h3 {
    font-size: clamp(16px, 3vh, 28px);
}

.testcase-header button {
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

.testcase-header button:hover {
    color: gray;
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

.testcase-items {
    display: flex;
    flex-direction: row;
    gap: 16px;
    width: 100%;
    justify-content: space-around;
    flex-wrap: wrap;
}

:deep(.custom-tooltip) {
    background: white;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    font-family: inherit;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
    min-width: 190px;
}

:deep(.tooltip-header) {
    padding-bottom: 6px;
    margin-bottom: 6px;
    border-bottom: 1px solid #f1f1f1;
}

:deep(.test-name) {
    font-weight: 600;
    color: #1a1a1a;
}

:deep(.tooltip-metric) {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 1px 0;
    line-height: 1.4;
}

:deep(.tooltip-metric .dot) {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}

:deep(.tooltip-metric .metric-label) {
    color: #555;
    flex: 1;
}

:deep(.tooltip-metric .metric-value) {
    font-weight: 700;
    color: #1a1a1a;
}

:deep(.tooltip-body) {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #f1f1f1;
}

:deep(.tooltip-body .row) {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    padding: 1px 0;
}

:deep(.tooltip-body .label) {
    color: #888;
}

:deep(.tooltip-body .value) {
    color: #333;
    font-weight: 500;
}

@media (max-width: 900px) {
    .testcase-items {
        display: flex;
        flex-direction: column;
        gap: 16px;
        justify-content: center;
        align-items: center;
    }

    .testcase-header {
        padding-bottom: 50px;
    }

}
</style>
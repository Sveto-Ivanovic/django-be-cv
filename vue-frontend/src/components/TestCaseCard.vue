<template>
    <n-card class="testcase-card-root" hoverable @click="HandleCardClick">


        <div class="card-header">
            <div>
                <h2 class="testcase-title" :title="props.test_case_name!">{{ props.test_case_name }}</h2>
                <span class="subtitle">Testcase Name:</span>
            </div>

            <div class="rows">
                <span class="rows-number">{{ props.number_of_testcases }}</span>
                <span class="rows-text">Rows</span>
            </div>
        </div>



        <div class="divider"></div>



        <div class="info-grid">

            <div class="info-item">
                <span class="label">QA Model</span>
                <span class="badge">{{ props.qa_model_used }}</span>
            </div>

            <div class="info-item">
                <span class="label">Eval Model</span>
                <span class="badge">{{ props.validation_model_used }}</span>
            </div>

            <div class="info-item">
                <span class="label">Created</span>
                <span>{{ props.created_at.slice(0, 10) }}</span>
            </div>

        </div>

        <div class="eval-result">
            <div class="metric-wrapper" v-if="props.aggregate_metadata && props.aggregate_metadata.answer_correctness">
                <span class="metric-label">Answer Correctness:</span>
                <span :class="props.aggregate_metadata.answer_correctness>0.6? 'metric-value-success' : 'metric-value-failiure'">{{ props.aggregate_metadata.answer_correctness.toFixed(2) }}</span>

            </div>

            <div class="metric-wrapper" v-if="props.aggregate_metadata && props.aggregate_metadata.answer_relevancy">
                <span class="metric-label">Answer Relevancy:</span>
                <span :class="props.aggregate_metadata.answer_relevancy>0.6? 'metric-value-success' : 'metric-value-failiure'">{{ props.aggregate_metadata.answer_relevancy.toFixed(2) }}</span>

            </div>

            <div class="metric-wrapper" v-if="props.aggregate_metadata && props.aggregate_metadata.context_recall">
                <span class="metric-label">Context Recall:</span>
                <span :class="props.aggregate_metadata.context_recall>0.6? 'metric-value-success' : 'metric-value-failiure'">{{ props.aggregate_metadata.context_recall.toFixed(2) }}</span>

            </div>


            <div class="metric-wrapper" v-if="props.aggregate_metadata && props.aggregate_metadata.faithfulness">
                <span class="metric-label">Faithfulness:</span>
                <span :class="props.aggregate_metadata?.faithfulness>0.6? 'metric-value-success' : 'metric-value-failiure'">{{ props.aggregate_metadata.faithfulness.toFixed(2) }}</span>

            </div>

        </div>
    </n-card>
</template>



<script setup lang="ts">
import { ref, computed } from 'vue'
import { GetAggregateItem } from '../services/testcase/types'
import { useRouter } from 'vue-router';

const props = withDefaults(defineProps<GetAggregateItem>(), {
    id: 'unknown',
    test_case_name: 'unknown',
    qa_model_used: 'unknown',
    aggregate_metadata: () => ({
        faithfulness: 0,
        answer_relevancy: 0,
        answer_correctness: 0,
        context_recall: 0,
    }),
    validation_model_used: 'unknown',
    created_at: 'unknown',
    number_of_testcases: 0
})

const router = useRouter()
function HandleCardClick() {
    router.push(`/testcase-statistics/${props.id}`)
}



</script>



<style scoped>
.testcase-card-root {
    width: min(500px, 100%);
    min-height: 260px;
    cursor: pointer;
    border-radius: 18px;
    transition: all .25s ease;
    background: linear-gradient(180deg, #ffffff, #fafafa);
    box-shadow: 3px 3px 8px 8px rgba(0, 0, 0, 0.08);

}

.testcase-card-root:hover {
    transform: translateY(-6px);
    box-shadow: 3px 16px 40px rgba(0, 0, 0, .15);
    border: 1px solid #4f46e5;
}

.testcase-card-root :deep(.n-card-content) {
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card-header h2 {
    margin: 0;
    font-size: 1.6rem;
    font-weight: 700;
}

.subtitle {
    color: #888;
    font-size: .9rem;
}

.rows {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: #4f46e5;
    color: white;
    padding: 12px 20px;
    border-radius: 14px;
}

.rows-number {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
}

.rows-text {
    opacity: .9;
    font-size: .8rem;
}

.divider {
    height: 1px;
    background: #ececec;
}

.info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}

.eval-result {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}

.metric-wrapper{
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.metric-label {
    color: gray;
    opacity: 0.7;
    font-weight: 600;
    font-size: 18px;
}

.metric-value-success {
    color: var(--text-color);
    padding: 8px;
    background-color: rgb(194, 235, 178);
    color: green;
    font-weight: 400;
    font-size: 14px;
    width: 30px;
    text-align: center;
    border-radius: 16px;
}

.metric-value-failiure {
    color: var(--text-color);
    padding: 8px;
    background-color: rgb(230, 172, 172);
    color: red;
    font-weight: 400;
    font-size: 14px;
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.full-width {
    grid-column: 1 / -1;
}

.label {
    color: #888;
    font-size: .85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .05em;
}

.badge {
    display: inline-block;
    width: fit-content;
    background: #eef2ff;
    color: #4338ca;
    padding: 6px 12px;
    border-radius: 999px;
    font-family: monospace;
    font-size: .9rem;
}

.testcase-title {
    max-width: 100%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.info-item p {
    margin: 0;
    color: #555;
    line-height: 1.5;
    word-break: break-word;
}
</style>
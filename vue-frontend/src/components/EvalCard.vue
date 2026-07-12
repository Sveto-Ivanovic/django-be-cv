<template>
    <div class="metric-card">

        <div class="metric-card-header">
            <span class="metric-card-title">Summary</span>
            <span class="metric-card-count">{{ numOfTests }} test{{ numOfTests === 1 ? '' : 's' }}</span>
        </div>

        <div class="seperator"></div>

        <div class="metric-row" v-for="metric in metrics" :key="metric.label">
            <div class="metric-label">{{ metric.label }}</div>
            <div class="metric-stats">
                <div class="stat">
                    <span class="stat-label">min</span>
                    <span class="stat-value" :class="scoreClass(metric.min)">{{ formatScore(metric.min) }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">avg</span>
                    <span class="stat-value" :class="scoreClass(metric.avg)">{{ formatScore(metric.avg) }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">max</span>
                    <span class="stat-value" :class="scoreClass(metric.max)">{{ formatScore(metric.max) }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

export interface MetricStat {
    avg: number | null;
    min: number | null;
    max: number | null;
}

const props = defineProps<{
    numOfTests: number;
    answerRelevancy: MetricStat;
    answerCorrectness: MetricStat;
    contextRecall: MetricStat;
    faithfulness: MetricStat;
}>();

const metrics = computed(() => [
    { label: 'Answer Relevancy', ...props.answerRelevancy },
    { label: 'Answer Correctness', ...props.answerCorrectness },
    { label: 'Context Recall', ...props.contextRecall },
    { label: 'Faithfulness', ...props.faithfulness },
]);

function scoreClass(value: number | null): string {
    if (value === null) {
        return 'score-red'; 
    }

    if (value < 0.5) return 'score-red';
    if (value < 0.8) return 'score-yellow';
    return 'score-green';
}

function formatScore(value: number | null): string {
    if(value===null) return '-'
    return Number.isFinite(value) ? value.toFixed(2) : '-';
}
</script>

<style scoped>
.metric-card {
    width: 100%;
    max-width: 500px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 16px;
    box-sizing: border-box;
    background-color: #fff;
}

.metric-card-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}

.metric-card-title {
    font-weight: 600;
    font-size: 16px;
}

.metric-card-count {
    font-size: 13px;
    color: #666;
}

.seperator {
    height: 0px;
    border-top: 1px solid #e0e0e0;
    margin: 12px 0;
}

.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;
    flex-wrap: wrap;
    gap: 8px;
}

.metric-row:last-child {
    border-bottom: none;
}

.metric-label {
    font-size: 14px;
    font-weight: 500;
    flex: 1 1 140px;
}

.metric-stats {
    display: flex;
    gap: 16px;
    flex: 1 1 180px;
    justify-content: flex-end;
}

.stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 40px;
}

.stat-label {
    font-size: 11px;
    color: #888;
    text-transform: uppercase;
}

.stat-value {
    font-size: 14px;
    font-weight: 600;
    padding: 1px 6px;
    border-radius: 4px;
}

.score-red {
    color: #a30000;
    background-color: #fdecea;
}

.score-yellow {
    color: #8a6d00;
    background-color: #fff7e0;
}

.score-green {
    color: #1e7a1e;
    background-color: #eaf7ea;
}

/* Mobile: stack label above stats, tighten spacing */
@media (max-width: 480px) {
    .metric-row {
        align-items: flex-start;
    }

    .metric-stats {
        width: 100%;
        justify-content: space-between;
    }
}
</style>
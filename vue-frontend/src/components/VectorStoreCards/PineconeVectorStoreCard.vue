<template>
    <n-card class="inde-card-root" hoverable @click="HandleCardClick(props.routeTo)">


        <div class="card-header">
            <div>
                <h2 class="index-title" :title="props.index_name">{{ props.index_name }}</h2>
                <span class="subtitle">Index Name</span>
            </div>

            <div class="rows">
                <span class="rows-number">{{ props.dimension }}</span>
                <span class="rows-text">Dimension</span>
            </div>
        </div>



        <div class="divider"></div>



        <div class="info-grid">

            <div class="info-item">
                <span class="label">Model</span>
                <span class="badge">{{ props.embed_model }}</span>
            </div>

            <div class="info-item">
                <span class="label">Metric</span>
                <span class="badge">{{ props.metric }}</span>
            </div>

            <div class="info-item">
                <span class="label">Vector Type</span>
                <span>{{ props.vector_type }}</span>
            </div>


        </div>
    </n-card>
</template>



<script setup lang="ts">
import { ref, computed } from 'vue'
import { IndexItem} from '../../services/vector_store/pinecone_indexes/types'
import { useRouter } from 'vue-router';

const props = withDefaults(defineProps<IndexItem & { routeTo: string }>(), {
    index_name: "unknown",
    metric: "unknown",
    vector_type: "unknown",
    dimension: 0,
    embed_model: "unknown",
})

const router = useRouter()
function HandleCardClick(to: string) {
    router.push({
        name: to
    })
}



</script>



<style scoped>

.inde-card-root {
    width: min(500px, 100%);
    min-height: 260px;
    cursor: pointer;
    border-radius: 18px;
    transition: all .25s ease;
    background: linear-gradient(180deg, #ffffff,  #fafafa);
    box-shadow: 3px 3px 8px 8px rgba(0, 0, 0, 0.08);

}

.inde-card-root:hover {
    transform: translateY(-6px);
    box-shadow: 3px 16px 40px rgba(0, 0, 0, .15);
    border: 1px solid #4f46e5;
}

.inde-card-root :deep(.n-card-content) {
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
    grid-template-columns: repeat(2, 1fr);
    gap: 18px;
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: 6px;
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

.index-title {
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
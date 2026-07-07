<template>
    <n-card class="namespace-card-root" hoverable @click="HandleCardClick(props.routeTo)">


        <div class="card-header">
            <div>
                <h2 class="namespace-title" :title="props.namespace">{{ props.namespace }}</h2>
                <span class="subtitle">Namespace</span>
            </div>

            <div class="rows">
                <span class="rows-number">{{ props.row_count }}</span>
                <span class="rows-text">Rows</span>
            </div>
        </div>



        <div class="divider"></div>



        <div class="info-grid">

            <div class="info-item">
                <span class="label">Model</span>
                <span class="badge">{{ props.model }}</span>
            </div>

            <div class="info-item">
                <span class="label">Table</span>
                <span class="badge">{{ props.supabase_table_name }}</span>
            </div>

            <div class="info-item">
                <span class="label">Created</span>
                <span>{{ props.created_at.slice(0, 10) }}</span>
            </div>

            <div class="info-item full-width" v-if="props.additional_info">
                <span class="label">Additional Info</span>
                <p>{{ props.additional_info }}</p>
            </div>

        </div>
    </n-card>
</template>



<script setup lang="ts">
import { ref, computed } from 'vue'
import { SupabaseNamespace, GetSupabaseNamespacesResponse } from '../../services/vector_store/supabase_namespaces/types'
import { useRouter } from 'vue-router';

const props = withDefaults(defineProps<SupabaseNamespace & { routeTo: string }>(), {
    namespace: "unknown",
    model: "unknown",
    row_count: 0,
    additional_info: "unknown",
    updated_at: "unknown",
    created_at: "unknown",
    supabase_table_name: "unknown"
})

const router = useRouter()
function HandleCardClick(to: string) {
    router.push(`/supabase/supabase-namespaces/${props.namespace}/${props.supabase_table_name}`)
}



</script>



<style scoped>

.namespace-card-root {
    width: min(500px, 100%);
    min-height: 260px;
    cursor: pointer;
    border-radius: 18px;
    transition: all .25s ease;
    background: linear-gradient(180deg, #ffffff,  #fafafa);
    box-shadow: 3px 3px 8px 8px rgba(0, 0, 0, 0.08);

}

.namespace-card-root:hover {
    transform: translateY(-6px);
    box-shadow: 3px 16px 40px rgba(0, 0, 0, .15);
    border: 1px solid #4f46e5;
}

.namespace-card-root :deep(.n-card-content) {
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

.namespace-title {
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
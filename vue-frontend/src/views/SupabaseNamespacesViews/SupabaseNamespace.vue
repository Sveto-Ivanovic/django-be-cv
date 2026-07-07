<template>
    <div class="supabase-header" v-if="!isFetching">
        <div>
            <h3>Supabase Namespaces</h3>
        </div>
        <div class="seperator"></div>
    </div>
    <div class="root-div">
        <div class="supabase-items" v-if="isSuccess && fetchedData && fetchedData?.length > 0 && !isFetching">
            <div v-for="value in fetchedData">
                <SupabaseVectorStoreCard :namespace="value.namespace" :additional_info="value.additional_info"
                    :created_at="value.created_at" :row_count="value.row_count"
                    :supabase_table_name="value.supabase_table_name" :updated_at="value.updated_at" :model="value.model"
                    :route-to="'Dashboard'"></SupabaseVectorStoreCard>
            </div>

        </div>
        <div class="no-namespace" v-else-if="isSuccess && fetchedData && fetchedData?.length == 0 && !isFetching"> No
            Supabase Namespaces found ... </div>
        <div class="loader" v-else-if="isFetching">
            <LoadingComponent></LoadingComponent>
        </div>
        <div class="error-event" v-else-if="isFetched && isError && !!fetchedData"> Error occured ...</div>
    </div>
</template>


<script setup lang="ts">
import { computed } from 'vue';
import { globalAPI } from '../../services'
import SkeletionLoader from '../../components/SkeletionLoader.vue';
import SupabaseVectorStoreCard from '../../components/VectorStoreCards/SupabaseVectorStoreCard.vue';
import LoadingComponent from '../../components/LoadingComponent.vue';

const { isFetching, isFetched, isSuccess, isError, data } = globalAPI.userSupabase.fetchSupabaseNamespaces()

const fetchedData = computed(() => {
    console.log(data.value?.data.response)
    if (data.value?.data.response && typeof data.value?.data.response === 'object') { return data.value?.data.response ?? [] }
})


</script>


<style scoped>
.loader {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.root-div {
    height: 100vh;
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

.supabase-header button {
    color: var(--text-color);
    font-size: 16px;
    border: none;
    font-weight: 500;
    background-color: transparent;
    cursor: pointer;
}

.arrow {
    font-size: 20px;
    font-weight: 600;
}

.supabase-header button:hover {
    color: gray;
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

.supabase-items {
    display: flex;
    flex-direction: row;
    gap: 16px;
    width: 100%;
    justify-content: space-around;
    flex-wrap: wrap;
}

@media (max-width: 900px) {
    .supabase-items {
        display: flex;
        flex-direction: column;
        gap: 16px;
        justify-content: center;
        align-items: center;
    }

    .supabase-header {
        padding-bottom: 50px;
    }

}
</style>
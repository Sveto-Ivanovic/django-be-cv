<template>
    <div class="root-div">
    <div class="supabase-items" v-if="isSuccess && fetchedData && fetchedData?.length > 0 && !isFetching">
        <div v-for="value in fetchedData">
            <SupabaseVectorStoreCard
                :namespace="value.namespace"
                :additional_info="value.additional_info"
                :created_at="value.created_at"
                :row_count="value.row_count"
                :supabase_table_name="value.supabase_table_name"
                :updated_at="value.updated_at"
                :model="value.model"
                :route-to="'Dashboard'"
            
            ></SupabaseVectorStoreCard>
        </div>

    </div>
    <div v-else-if="isSuccess && fetchedData &&fetchedData?.length > 0 && !isFetching"> no data </div>
    <div v-else-if="isFetching">
        <SkeletionLoader></SkeletionLoader>
    </div>
    <div v-else-if="isFetched && isError && !!fetchedData"> error here</div>
</div>
</template>


<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { globalAPI } from '../services';
import { GetSupabaseNamespaceRecordsRequest } from '../services/vector_store/supabase_namespaces/types';
import SkeletionLoader from '../components/SkeletionLoader.vue';
import SupabaseVectorstore from '../components/VectorStoreCards/SupabaseVectorstore.vue';
import SupabaseVectorStoreCard from '../components/VectorStoreCards/SupabaseVectorStoreCard.vue';

const { isFetching, isFetched, isSuccess, isError, data } = globalAPI.userSupabase.fetchSupabaseNamespaces()

const fetchedData = computed(() => {
    console.log(data.value?.data.response)
    if (data.value?.data.response && typeof data.value?.data.response === 'object') { return data.value?.data.response ?? [] }
})


</script>


<style scoped>
    .root-div{
        height: 100vh;
    }

    .supabase-items{
        display: flex;
        flex-direction: row;
        gap: 16px;
        width: 100%;
        justify-content: space-around;
        flex-wrap: wrap;
    }

@media (max-width: 900px) {
      .supabase-items{
        display: flex;
        flex-direction: column;
        gap: 16px;
        justify-content: center;
        align-items: center;
    }
}
</style>
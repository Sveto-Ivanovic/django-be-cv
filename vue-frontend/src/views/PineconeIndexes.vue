<template>
    <div class="root-div">
    <div class="pinecone-items" v-if="isSuccess && fetchedData && fetchedData?.length > 0 && !isFetching">
        <div v-for="value in fetchedData">
            <PineconeVectorStoreCard
                :index_name="value.index_name"
                :embed_model="value.embed_model"
                :dimension="value.dimension"
                :vector_type="value.vector_type"
                :metric="value.metric"
                :route-to="'Dashboard'"
            
            ></PineconeVectorStoreCard>
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
import SkeletionLoader from '../components/SkeletionLoader.vue';
import PineconeVectorStoreCard from '../components/VectorStoreCards/PineconeVectorStoreCard.vue';

const { isFetching, isFetched, isSuccess, isError, data } = globalAPI.userPinecone.fetchPineconeIndexes()

const fetchedData = computed(() => {
    console.log(data.value?.data.response)
    if (data.value?.data.response && typeof data.value?.data.response === 'object') { return data.value?.data.response ?? [] }
})


</script>


<style scoped>
    .root-div{
        height: 100vh;

    }

    .pinecone-items{
        display: flex;
        flex-direction: row;
        gap: 16px;
        width: 100%;
        justify-content: space-around;
        flex-wrap: wrap;
    }

@media (max-width: 900px) {
      .pinecone-items{
        display: flex;
        flex-direction: column;
        gap: 16px;
        justify-content: center;
        align-items: center;
    }
}
</style>
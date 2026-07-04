<template>
    <div class="skeleton-container">
    <div  class="skeleton-div" v-for="num in number_of_rows" key="num"> 
        <n-skeleton text :repeat="2" /> <n-skeleton text style="width: 100%" />
        <n-skeleton text :repeat="0" /> <n-skeleton text style="width: 70%" />
    </div>
</div>
</template>

<script setup lang="ts">
import { useWindowSize } from '@vueuse/core'
import { computed } from 'vue';
const { width, height } = useWindowSize()

const row_height = 130

let number_of_rows = computed(() => Math.ceil(height.value / row_height))

</script>

<style scoped>
.skeleton-container{
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.skeleton-div{
    padding-left: 16px;
    padding-right: 16px;
}
</style>
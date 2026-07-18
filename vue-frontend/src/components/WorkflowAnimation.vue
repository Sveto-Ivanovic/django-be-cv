<template>
    <div v-if="mounted">
        <div v-if="isMobile" class="pipeline">
            <div class="step">
                <Vue3Lottie animationLink="/animations/PDF Generating.json" :height="100" :width="100" />
                <span>PDF request</span>
            </div>

            <div>
                <Vue3Lottie class="arrow" animationLink="/animations/arrow (2).json" :height="60" :width="60" />
            </div>

            <div class="step">
                <Vue3Lottie animationLink="/animations/artificial intelligence.json" :height="120" :width="120" />
                <span>Embed</span>
            </div>

            <div>
                <Vue3Lottie class="arrow" animationLink="/animations/arrow (2).json" :height="60" :width="60" />
            </div>

            <div class="evaluate">
                <span class="title">Evaluate</span>
                <span class="metrics">
                    Accuracy: 0.94 <br />
                    Precision: 0.91 <br />
                    Recall: 0.89
                </span>
            </div>

        </div>
        <div v-else class="pipeline">
            <div class="step">
                <Vue3Lottie animationLink="/animations/PDF Generating.json" :height="100" :width="100" />
                <span>PDF request</span>
            </div>

            <div>
                <Vue3Lottie class="arrow" animationLink="/animations/arrow.json" :height="60" :width="60" />
            </div>

            <div class="step">
                <Vue3Lottie animationLink="/animations/artificial intelligence.json" :height="120" :width="120" />
                <span>Embed</span>
            </div>

            <div>
                <Vue3Lottie class="arrow" animationLink="/animations/arrow.json" :height="60" :width="60" />
            </div>

            <div class="evaluate">
                <span class="title">Evaluate</span>
                <span class="metrics">
                    Accuracy: 0.94 <br />
                    Precision: 0.91 <br />
                    Recall: 0.89
                </span>
            </div>

        </div>


        <div class="dashboard">
            <VueApexCharts type="bar" :height="height_bar" :width="width_bar" :options="options" :series="series">

            </VueApexCharts>
            <VueApexCharts type="line" :height="height_line" :width="width_line" :options="options_line" :series="series_line">

            </VueApexCharts>


        </div>
    </div>
</template>



<script setup lang="ts">

import { ref, onMounted, watchEffect, computed, shallowRef } from "vue";
import VueApexCharts from 'vue3-apexcharts'
import type { ApexOptions } from 'apexcharts'
import { useWindowSize } from '@vueuse/core'

const Vue3Lottie = shallowRef<any>(null)
const mounted = ref(false)
onMounted(async () => { const mod = await import('vue3-lottie')
    Vue3Lottie.value = mod.Vue3Lottie
    mounted.value = true
})

const options = ref<ApexOptions>({
    chart: { type: 'bar',
        toolbar: {
      show: true, 
      tools: {
        download: false,
    }}
     },
    plotOptions: {
        bar: { horizontal: false }
    }
})

const series = ref([{
    data: [
        {
            x: 'Accuracy',
            y: 0.94,
            goals: [{ name: 'Expected', value: 1, strokeColor: '#775DD0' }]
        },
        {
            x: 'Precision',
            y: 0.91,
            goals: [{ name: 'Expected', value: 1, strokeColor: '#775DD0' }]
        },
        {
            x: 'Recall',
            y: 0.89,
            goals: [{ name: 'Expected', value: 1, strokeColor: '#775DD0' }]
        }
    ]
}])


const options_line = ref<ApexOptions>({
    chart: {
        type: 'line',
        zoom: {
            enabled: false,
        },
              toolbar: {
      show: true, 
      tools: {
        download: false,
    }}
    },
    dataLabels: {
        enabled: false,
    },
    stroke: {
        width: [5, 7, 5],
        curve: 'straight',
        dashArray: [0, 0, 0],
    },
    title: {
        text: 'Evaluation Progress',
        align: 'left',
    },
    markers: {
        size: 4,
        hover: {
            sizeOffset: 6,
        },
    },
    xaxis: {
        categories: [
            'Epoch 1',
            'Epoch 2',
            'Epoch 3',
            'Epoch 4',
            'Epoch 5',
            'Epoch 6',
            'Epoch 7',
            'Epoch 8',
            'Epoch 9',
            'Epoch 10',
            'Epoch 11',
            'Epoch 12',
        ],
    },
    tooltip: {
        y: [
            {
                title: {
                    formatter: function (val) {
                        return val + ' Metric'
                    },
                },
            },
            {
                title: {
                    formatter: function (val) {
                        return val + ' Metric'
                    },
                },
            },
            {
                title: {
                    formatter: function (val) {
                        return val + ' Metric'
                    },
                },
            },
        ],
    },
    grid: {
        borderColor: '#f1f1f1',
    },
})

const series_line = ref([
            {
                name: 'Accuracy',
                data: [0.91, 0.92, 0.94, 0.93, 0.95, 0.94, 0.96, 0.95, 0.94, 0.97, 0.96, 0.94],
            },
            {
                name: 'Precision',
                data: [0.88, 0.89, 0.91, 0.90, 0.92, 0.91, 0.93, 0.92, 0.91, 0.94, 0.93, 0.91],
            },
            {
                name: 'Recall',
                data: [0.84, 0.86, 0.89, 0.88, 0.90, 0.89, 0.91, 0.90, 0.89, 0.92, 0.91, 0.89],
            }
]);


let height_bar = computed(()=>{
     if (width.value <= 768) {
        return 300;
    }
    else if(width.value <= 1200) {
        return 400;
    }
    else{
        return 450;
    }
})
let width_bar = computed(()=>{
         if (width.value <= 768) {
        return 300;
    }
    else if(width.value <= 1200) {
        return 400;
    }
    else{
        return 450;
    }
})
let height_line = computed(()=>{
         if (width.value <= 768) {
        return 300;
    }
    else if(width.value <= 1200) {
        return 400;
    }
    else{
        return 450;
    }
})
let width_line = computed(()=>{

    if (width.value <= 768) {
        return 300;
    }
    else if(width.value <= 1200) {
        return 500;
    }
    else{
        return 550;
    }
})

let isMobile = ref(false)
const { width, height } = useWindowSize()

watchEffect(() => {
    if (width.value <= 768) {
        isMobile.value = true
    }
    else {
        isMobile.value = false
    }
})

</script>

<style scoped>
.pipeline {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 24px;
}

.step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
}

.step span {
    font-size: 13px;
    color: var(--text-color);
}


/* Evaluate box */
.evaluate {
    width: 150px;
    min-height: 100px;
    border: 1px solid rgba(120, 120, 255, 0.4);
    border-radius: 14px;
    background: rgba(120, 120, 255, 0.08);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 12px;
    box-shadow: 0 0 20px rgba(120, 120, 255, 0.15);
    color: black;
    animation: pulse 2s infinite;
}

.evaluate .title {
    font-size: 18px;
    font-weight: 600;
}

.metrics {
    font-size: 12px;
    text-align: center;
    opacity: 0.8;
}

.dashboard {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

@keyframes pulse {
    0% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.1);
    }

    100% {
        transform: scale(1);
    }
}

@media (max-width: 768px) {

    .pipeline {
        flex-direction: column;
    }

    .dashboard{
        flex-direction: column;
    }
}
</style>
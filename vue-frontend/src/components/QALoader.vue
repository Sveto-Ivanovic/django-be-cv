<template>
    <div class="loading-component">

        <div class="circle-container">
            <div class="circle1" :style="`width: ${props.circle_size}; height: ${props.circle_size};`"></div>
            <div class="circle2"></div>
            <div class="circle3"></div>
        </div>

    </div>

</template>



<script setup lang="ts">
const props = withDefaults(defineProps<{
    circle_size: string
}>(),
    {
        circle_size: '20px'
    }
)


</script>




<style scoped>
.loading-component {
    opacity: 80%;
    background-color: transparent;
    display: flex;
    justify-content: center;
    align-items: center;
}

.circle-container {

    padding: 16px;
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    align-items: center;
    transform: y;
}

@keyframes snake {

    0%,
    80%,
    100% {
        transform: translateY(-4px);
        opacity: 0.8;
    }

    40% {
        transform: translateY(4px);
        opacity: 1;
    }
}

.circle1,
.circle2,
.circle3 {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: linear-gradient(90deg,
            rgb(8, 56, 75),
            rgb(189, 255, 255),
            rgb(143, 0, 112));
    animation: snake 1.2s infinite ease-in-out;
}

.circle2 {
    animation-delay: 0.2s;
}

.circle3 {
    animation-delay: 0.4s;
}
</style>
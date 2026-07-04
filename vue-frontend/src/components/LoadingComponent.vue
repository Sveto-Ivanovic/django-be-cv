<template>
    <div class="loading-component">

        <div class="circle-container">
            <div class="circle1"></div>
            <div class="circle2"></div>
            <div class="circle3"></div>
        </div>

    </div>

</template>



<script setup lang="ts">


</script>




<style scoped>
.loading-component {
    height: 100vh;
    width: 100vw;
    opacity: 80%;
    background-color: white;
    display: flex;
    justify-content: center;
    align-items: center;
}

.circle-container {

    width: 200px;
    padding: 16px;
    height: 200px;
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    align-items: center;
}

@keyframes pulse {
    0%,
    80%,
    100% {
        transform: scale(0.7);
        opacity: 0.4;
    }

    40% {
        transform: scale(1.3);
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
            rgba(42, 123, 155, 1),
            rgba(87, 199, 133, 1),
            rgba(237, 221, 83, 1));
    animation: pulse 1.2s infinite ease-in-out;
}

.circle2 {
    animation-delay: 0.2s;
}

.circle3 {
    animation-delay: 0.4s;
}
</style>
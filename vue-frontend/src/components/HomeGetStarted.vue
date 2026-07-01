<template>
    <div class="get-started-class">
        <div class="get-started-class-header">
            Ready to Build Better AI Systems?
        </div>

        <div class="get-started-class-body">
            Start evaluating, comparing, and improving your AI workflows with your own infrastructure. Connect your
            models, test performance, and get actionable insights — all while keeping your data under your control.
        </div>

        <button class="get-started-button" @click="redirectToLogin">
            Get Started

            <div class="icons">
                <ArrowForward />
            </div>

        </button>
    </div>
</template>


<script setup lang="ts">
import { ArrowForward } from '@vicons/ionicons5'
import { useRouter } from 'vue-router'

const router = useRouter()
function redirectToLogin() {
    router.push('/login')
}

</script>


<style>
.get-started-button {
    width: 50%;
    background-color: var(--button-background-color);
    color: var(--text-color);
    padding-top: 16px;
    padding-bottom: 16px;
    border-radius: 24px;
    font-size: 20px;
    font-family: "Inter", sans-serif;
    font-weight: 500;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 16px;
    border: 2px solid var(--button-background-border-color);
    box-shadow: 3px 3px 16px 8px rgba(0, 0, 0, 0.2);
    cursor: pointer;
    transition: background-color 0.25s ease, border-color 0.25s ease, transform 0.15s ease;
}

.get-started-button:hover {
    background-color: var(--button-background-color-hover);
    color: var(--text-color);
    border-color: var(--button-background-border-color-hover);
    transform: translateY(-2px);
}

.get-started-button:active {
    transform: translateY(0);
}

.get-started-class {
    display: flex;
    flex-direction: column;
    width: 100%;
    justify-content: center;
    align-items: center;
    padding-top: 32px;
    padding-bottom: 32px;
    gap: 32px;
}

.icons {
    width: 30px;
    height: 30px;
}

.get-started-class-header {
    font-family: "Manrope", sans-serif;
    font-size: clamp(1.5rem, 3vw, 2.5rem);
    font-weight: 600;
    line-height: 1.1;
    letter-spacing: -0.04em;
    width: min(80%, 900px);
    color: var(--hero-headline-color);
    text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3);
    text-align: center;
}

.get-started-class-body {
    font-family: "Inter", sans-serif;
    font-size: clamp(0.8rem, 2vw, 1.2rem);
    font-weight: 300;
    line-height: 1.7;
    width: min(80%, 750px);
    color: var(--hero-subheadline-color);
    text-align: center;
}
</style>
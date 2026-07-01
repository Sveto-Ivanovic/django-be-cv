<template>
  <Hero headline="Build, Evaluate, and Compare AI Systems with Your Own Infrastructure"
    subheadline="Bring your own API keys, connect your own vector database, upload benchmark datasets, and measure how different LLMs perform using objective evaluation metrics—all while keeping full control over your data.">
  </Hero>
  <Animation></Animation>
<div ref="target" style="min-height: 1px">
  <GetStarted 
    v-if="targetIsVisible" 
   </GetStarted>
</div>
</template>




<script setup lang="ts">
import Animation from '../components/WorkflowAnimation.vue'
import { ref, defineAsyncComponent } from 'vue'
import Hero  from '../components/HeroSection.vue'
import GetStarted from '../components/HomeGetStarted.vue'
import { useIntersectionObserver } from '@vueuse/core'
import { shallowRef, useTemplateRef } from 'vue'

const target = useTemplateRef('target')
const targetIsVisible = shallowRef(false)

const { stop } = useIntersectionObserver(
  target,
  (entries: IntersectionObserverEntry[]) => {
    if (entries[0]?.isIntersecting) {
      targetIsVisible.value = true
      stop()
    }
  },
)

</script>



<style scoped>
.headline {
  color: var(--text-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}
</style>
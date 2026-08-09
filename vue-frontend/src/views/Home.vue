<template>
  <div style="padding-bottom: 32px; display: flex; flex-direction: column; align-items: center;">
    <Testora :size="testora_letter_size" :exclude-icon="true" :include-subtitle="false"></Testora>
    <p class="tagline">Rigorous evaluation infrastructure for LLM systems</p>
  </div>
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
import Hero  from '../components/HeroSection.vue'
import GetStarted from '../components/HomeGetStarted.vue'
import { useIntersectionObserver } from '@vueuse/core'
import { computed, shallowRef, useTemplateRef } from 'vue'
import Testora from '../components/Testora.vue'

const target = useTemplateRef('target')
const targetIsVisible = shallowRef(false)
import { useWindowSize } from '@vueuse/core'


const { stop } = useIntersectionObserver(
  target,
  (entries: IntersectionObserverEntry[]) => {
    if (entries[0]?.isIntersecting) {
      targetIsVisible.value = true
      stop()
    }
  },
)

const { width } = useWindowSize()
const testora_letter_size = computed(() => {
  if (width.value < 640) {
    return 50
  } else if (width.value < 1024) {
    return 80
  } else {
    return 100
  }
})

</script>


<style scoped>
.headline {
  color: var(--text-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.tagline {
  margin-top: 12px;
  font-size: 1.2rem;
  font-weight: 500;
  letter-spacing: 0.02em;
  text-wrap: wrap;
  padding-left: 24px;
  padding-right: 24px;
  color: var(--text-secondary, #6b6b7a);
  text-align: center;
}
</style>
<template>
  <n-popover trigger="hover" :width="popoverWidth" placement="bottom">

    <template #trigger>
      <n-button quaternary circle class="info-trigger" aria-label="Show info">
        <n-icon size="18">
          <Information />
        </n-icon>
      </n-button>
    </template>

    <div class="popover">
      <pre class="json">{{ content }}</pre>
    </div>
  </n-popover>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Information } from '@vicons/ionicons5';

const props = withDefaults(
  defineProps<{
    content: string;
  }>(),
  {
    content: 'Example content',
  }
);

const popoverWidth = computed(() =>
  typeof window !== 'undefined' && window.innerWidth < 480
    ? Math.min(window.innerWidth - 150, 320)
    : 420
);
</script>

<style scoped>
.info-trigger {
  color: #9a9a9a;
  transition: color 0.15s ease, background-color 0.15s ease;
}

.info-trigger:hover {
  color: #36ad6a;
  background-color: rgba(54, 173, 106, 0.08);
}

.popover {
  max-width: 100%;
}

.json {
  margin: 0;
  padding: 12px 14px;
  border-radius: 8px;
  background: #f7f7f8;
  border: 1px solid #ececec;
  font-family: 'SFMono-Regular', Consolas, monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
  word-break: break-word;
  overflow: auto;
  max-height: 360px;
}

</style>
<template>
  <RouterLink :to="{ name: routeName }" custom v-slot="{ navigate }">
    <div
      class="action-box"
      role="button"
      tabindex="0"
      @click="() => navigate()"
    >
      <p class="action-box-text">{{ text }}</p>
      <span class="action-box-arrow" aria-hidden="true">→</span>
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
interface Props {
  text: string
  routeName: string
}

defineProps<Props>()
</script>

<style scoped>
.action-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
  max-width: 480px;
  padding: 1rem 1.25rem;
  border: 1px solid #e2e2e7;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  text-decoration: none;
  color: inherit;
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
  box-sizing: border-box;
}

.action-box:hover {
  border-color: #6366f1;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.15);
  transform: translateY(-2px);
}

.action-box:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(99, 102, 241, 0.12);
}

.action-box:focus-visible {
  outline: 2px solid #6366f1;
  outline-offset: 2px;
}

.action-box-text {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.4;
  color: #1f2937;
}

.action-box-arrow {
  flex-shrink: 0;
  font-size: 1.1rem;
  color: #6366f1;
  transition: transform 0.15s ease;
}

.action-box:hover .action-box-arrow {
  transform: translateX(4px);
}

@media (max-width: 640px) {
  .action-box {
    max-width: 100%;
    padding: 0.875rem 1rem;
  }

  .action-box-text {
    font-size: 0.9rem;
  }
}
</style>
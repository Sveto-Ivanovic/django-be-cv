<template>
  <div class="testora-root">
    <div class="testora-logo" :style="{ fontSize: `${size}px` }">

      <span class="logo-icon">◈</span>

      <div v-if="!iconOnly" class="logo-text">
        <span class="primary">TESTORA</span>

        <span v-if="includeSubtitle" class="secondary">
          AI Testing Platform
        </span>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: number;
  includeSubtitle?: boolean;
  iconOnly?: boolean;
}

withDefaults(defineProps<Props>(), {
  size: 24,
  includeSubtitle: true,
  iconOnly: false,
});
</script>

<style scoped>
.testora-root{
    display: flex;
    width: 100%;
    justify-content: center;
    align-items: center;
}

.testora-logo {
  display: flex;
  align-items: center;
  gap: 0.6em;
  user-select: none;
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.6em;
  height: 1.6em;
  border-radius: 14px;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  font-size: 0.8em;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.35);
}

.primary {
  font-weight: 900;
  letter-spacing: 0.08em;
  background: linear-gradient(
    90deg,
    #22c55e,
    #06b6d4,
    #a855f7
  );
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  -webkit-text-fill-color: transparent;
}

.secondary {
  margin-top: 0.35em;
  font-size: 0.38em;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #6b7280;
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1;
}
</style>
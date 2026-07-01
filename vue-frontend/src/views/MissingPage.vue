<template>
  <div class="not-found">
    <h1>404</h1>
    <h2>Page Not Found</h2>
    <p>
      The page you're looking for doesn't exist or is still under development.
    </p>
  </div>
</template>

<script setup lang="ts">
// No logic needed
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  text-align: center;
  padding: 2rem;
  color: #374151;
}

h1 {
  font-size: 5rem;
  margin: 0;
  font-weight: 700;
  color: #111827;
}

h2 {
  margin: 0;
  font-size: 1.75rem;
}

p {
  margin: 0;
  max-width: 400px;
  color: #6b7280;
}
</style>
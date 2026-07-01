<template>
  <div class="hero">
    <div class="headline"> {{ headline }} </div>
    <div class="subheadline">{{ subheadline }}</div>
  </div>
</template>




<script setup lang="ts">

const props = defineProps(['headline', 'subheadline'])

</script>



<style scoped>
.hero {
  padding-top: 30px;
  color: var(--text-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  gap: 20px;
}

.headline {
  font-family: "Manrope", sans-serif;
  font-size: clamp(2rem, 5vw, 4.5rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.04em;
  width: min(80%, 900px);
  color: var(--hero-headline-color);
  text-shadow: 3px 3px 16px rgba(0, 0, 0, 0.5);
  text-align: center;
}

.subheadline {
  font-family: "Inter", sans-serif;
  font-size: clamp(1.1rem, 2vw, 1.35rem);
  font-weight: 400;
  line-height: 1.7;
  width: min(80%, 750px);
  color: var(--hero-subheadline-color);
  text-align: center;
}

@media(max-width:768px) {
  .hero {
    padding-top: 10px;
  }
}
</style>
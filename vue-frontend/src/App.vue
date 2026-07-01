<template>
  <div>
    <header>

      <div class="wrapper">
        <NavBar v-if="showMenuBar"></NavBar>
      </div>
    </header>
    <div class="view-content"  :class="{ 'no-margin': !showMenuBar }">
      <RouterView />
    </div>
  </div>
</template>




<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import NavBar from './components/CustomNavBar.vue'
import { ref, watchEffect } from 'vue';

let route = useRoute()
let showMenuBar = ref(true)
const allowed_routes= ['Home', 'Contact', 'About']


console.log(import.meta.env.VITE_BE_HOST)
watchEffect(()=>{

  if(route.name && typeof(route.name) === "string" && allowed_routes.includes(route.name)){
    showMenuBar.value = true
  }
  else{
    showMenuBar.value = false
  }


})


</script>

<style>
.view-content {
  margin-top: 150px;
  margin-bottom: 150px;
}

.no-margin {
  margin-top: 0;
  margin-bottom: 0;
}
</style>

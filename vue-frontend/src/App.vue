<template>
  <div v-if="envelop_with_sidebar === false" :class="{ 'bgcolor-body': !envelop_with_sidebar }">
    <div class="wrapper">
      <NavBar v-if="showMenuBar"></NavBar>
    </div>
    <div class="view-content" :class="{ 'no-margin': !showMenuBar }">
      <RouterView />
    </div>
  </div>
  <div v-else>
    <div v-if="isFetched">
      <SideBar>
        <RouterView />
      </SideBar>

    </div>
    <div v-else>

      <LoadingComponent></LoadingComponent>

    </div>
  </div>
</template>




<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import NavBar from './components/CustomNavBar.vue'
import { ref, watchEffect } from 'vue';
import SideBar from './components/DashboardSidebarComponent.vue'
import { useUserStore } from './stores/user_store/index.js';
import { globalAPI } from './services/index.js';
import LoadingComponent from './components/LoadingComponent.vue'

let route = useRoute()
let showMenuBar = ref(true)
let envelop_with_sidebar = ref(false)
const allowed_routes = ['Home', 'Contact', 'About']
const dashboard_routes = ['Dashboard', 'Profile', 'SupabaseEmbed', 'PineconeEmbed', 
'SupabaseNameSpaces', 'PineconeIndexes', 'SupabaseNamespaceRecords', 'PineconeIndexRecords', 'PineconeCreateIndex', 'TestCaseResults',
'TestCaseCreate', 'TestCaseResultStatistics'
]
const userStore = useUserStore()

watchEffect(() => {
  if (route.name && typeof (route.name) === "string" && allowed_routes.includes(route.name)) {
    showMenuBar.value = true
  }
  else {
    showMenuBar.value = false
  }
})


watchEffect(() => {
  if (route.name && typeof (route.name) === "string" && dashboard_routes.includes(route.name)) {
    envelop_with_sidebar.value = true
  }
  else {
    envelop_with_sidebar.value = false
  }
})


const { data, isLoading, isFetched } = globalAPI.userManagment.fetchUserInfo()


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

.bgcolor-body {
  background-color: transparent;
}
</style>

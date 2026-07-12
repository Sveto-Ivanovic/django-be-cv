<template>

<n-config-provider :theme-overrides="themeOverrides">

    <div class="root">
        <n-layout has-sider>


            <n-layout-sider class="sidebar"  collapse-mode="width" :collapsed="isMobile? true : undefined" :collapsed-width="60" :width="300" :show-trigger="!isMobile? 'bar' : false"
                @update:collapsed="handleCollapse">
                <Testora :icon-only="!isExpanded"></Testora>
                <n-menu  dropdown-placement="'right-start'" class="menu-wrapper" :options="menuOptions" @update:value="handleUpdateValue" />

                 
                <n-menu class="menu-wrapper-profile" :options="menuOptionsProfile" @update:value="handleUpdateValueProfile" />
            </n-layout-sider>



            <n-layout class="content-class" :style="{ marginLeft: isMobile || !isExpanded? '60px' : '300px' }">
                <n-layout-header>
                    <slot name="header"></slot>
                </n-layout-header>



                <n-layout-content content-style="padding: 24px; height: 100%;">
                    <slot></slot>
                </n-layout-content>



                <n-layout-footer>
                    <slot name="footer"></slot>
                </n-layout-footer>
            </n-layout>



        </n-layout>

    </div>


</n-config-provider>

</template>


<script setup lang="ts">
import type { Component } from 'vue'
import type { MenuOption } from 'naive-ui'
import {
    HomeOutline as HomeIcon,
    ServerOutline as ServerIcon,
    StatsChartOutline as StatsChartIcon,
    PersonCircleOutline as PersonCircleIcon,
    LogOutOutline as LogOutIcon,
    CloudUploadOutline as UploadIcon,
    AddCircleOutline as AddIcon
} from '@vicons/ionicons5'
import { NIcon } from 'naive-ui'
import { computed, h, ref } from 'vue'
import { RouterLink } from 'vue-router'
import Testora from './Testora.vue'
import { useWindowSize } from '@vueuse/core'
import { globalAPI } from '../services/index.js'
import router from '../router/index.js'


const {mutateAsync: logoutUser} = globalAPI.userManagment.logOutUser()
function renderIcon(icon: Component) {
    return () => h(NIcon, null, { default: () => h(icon) })
}

let menuOptions: MenuOption[] = [
    {
        label: () =>
            h(
                RouterLink,
                {
                    to: {
                        name: 'Dashboard',
                    }
                },
                { default: () => 'Dashboard' }
            ),
        key: 'go-to-dashboard',
        icon: renderIcon(HomeIcon)
    },
    {
        key: 'divider-1',
        type: 'divider',
        props: {
            style: {
                paddingLeft: '6px',
                paddingRight: '6px',
                borderBottom: '2px solid black',
                width: '80%'
            }
        }
    },
    {
        label: 'Vector Stores',
        key: 'vector-stores',
        icon: renderIcon(ServerIcon),
        children: [
            {
                type: 'group',
                label: 'Supabase',
                key: 'supabase-group',
                children: [
                    {
                        label: () =>
                            h(
                                RouterLink,
                                {
                                    to: {
                                        name: 'SupabaseNameSpaces',
                                    }
                                },
                                { default: () => 'Supabase Name Spaces' }
                            ),
                        key: 'go-to-supabase-namespaces',
                        icon: renderIcon(ServerIcon)
                    },
                     {
                        label: () =>
                            h(
                                RouterLink,
                                {
                                    to: {
                                        name: 'SupabaseEmbed',
                                    }
                                },
                                { default: () => 'Embed into Supabase' }
                            ),
                        key: 'go-to-supabase-embed',
                        icon: renderIcon(UploadIcon)
                    }
                ]

            },
            {
                type: 'group',
                label: 'Pinecone',
                key: 'pinecone-group',
                children: [
                    {
                        label: () =>
                            h(
                                RouterLink,
                                {
                                    to: {
                                        name: 'PineconeIndexes',
                                    }
                                },
                                { default: () => 'Pinecone Indexes' }
                            ),
                        key: 'go-to-pinecone-namespaces',
                        icon: renderIcon(ServerIcon)
                    },
                     {
                        label: () =>
                            h(
                                RouterLink,
                                {
                                    to: {
                                        name: 'PineconeEmbed',
                                    }
                                },
                                { default: () => 'Embed into Pinecone' }
                            ),
                        key: 'go-to-pinecone-embed',
                        icon: renderIcon(UploadIcon)
                    }
                ]

            }
        ]
    },
    {
        label: () =>
            h(
                RouterLink,
                {
                    to: {
                        name: 'TestCaseResults',
                    }
                },
                { default: () => 'Testcase Results' }
            ),
        key: 'go-to-testcase',
        icon: renderIcon(StatsChartIcon)

    },
    {
        label: () =>
            h(
                RouterLink,
                {
                    to: {
                        name: 'TestCaseCreate',
                    }
                },
                { default: () => 'Create Testcase' }
            ),
        key: 'go-to-create-testcase',
        icon: renderIcon(AddIcon)

    },

]

let menuOptionsProfile: MenuOption[] = [
{
        label: () =>
            h(
                RouterLink,
                {
                    to: {
                        name: 'Profile',
                    }
                },
                { default: () => 'Profile' }
            ),
        key: 'go-to-profile',
        icon: renderIcon(PersonCircleIcon)

    },
    {
        label: 'Log Out',
        key: 'go-to-home-logout',
        icon: renderIcon(LogOutIcon)

    }
]

let isExpanded = ref(true)
const { width, height } = useWindowSize()
function handleCollapse(collapsed: boolean) {
    isExpanded.value = !collapsed
}
let isMobile = computed(()=>{
if(width.value <= 900) {
        isExpanded.value=false
        return true;
    }
    else{
        return false;
    }
})
function handleUpdateValue(key: string, item: MenuOption) {
    console.log(`[onUpdate:value]: ${JSON.stringify(key)}`)
}
async function handleUpdateValueProfile(key: string, item: MenuOption) {
    console.log(`[onUpdate:value]: ${JSON.stringify(key)}`)
    if(key==="go-to-home-logout"){
        const response = await logoutUser()
        router.push({name: "Home"})
    }
}

const themeOverrides = {
  Menu: {
    itemColorActive: 'transparent',
    itemColorActiveHover: 'transparent',
    itemColorActiveCollapsed: 'transparent',
    itemTextColorActive: 'inherit',
    itemTextColorActiveHover: 'inherit',
    itemIconColorActive: 'inherit',
    itemIconColorActiveHover: 'inherit',
    itemTextColorChildActive: 'inherit',
    itemIconColorChildActive: 'inherit',
  }
}


</script>



<style scoped>
.sidebar {
   height: 100%;
    border: 2px solid var(--sidebar-border-color);
    background-color: var(--sidebar-background-color);
    color: var(--sidebar-text-color);
    position: fixed;
}

.sidebar :deep(.n-layout-sider-scroll-container) {
    display: flex;
    gap: 32px;
    flex-direction: column;
    padding-top: 32px;

}

.content-class{
    overflow-y: scroll;
    transition: margin-left 0.3s ease;
    height: 100%;
}

.menu-wrapper {
    height: 100%;
    display: flex;
    align-items: center;
    flex-direction: column;
    position: relative;
    width: 100%
}

.menu-wrapper :deep(.n-menu-item) {
    width: 100%;
    align-items: center;
    display: flex;
    justify-content: center;
}


.menu-wrapper :deep(.n-submenu) {
    width: 100%;
    align-items: center;
    display: flex;
    justify-content: center;
    flex-direction: column;
}

.menu-wrapper :deep(.n-menu-item-content) {
    width: 100%;
    align-items: center;
    display: flex;
    justify-content: flex-start;
}


.menu-wrapper-profile {
    height: 150px;
    display: flex;
    align-items: center;
    flex-direction: column;
    justify-content: flex-end;
    width: 100%
}

.menu-wrapper-profile :deep(.n-menu-item) {
    width: 100%;
    align-items: center;
    display: flex;
    justify-content: center;
}


.menu-wrapper-profile :deep(.n-submenu) {
    width: 100%;
    align-items: center;
    display: flex;
    justify-content: center;
    flex-direction: column;
}

.menu-wrapper-profile :deep(.n-menu-item-content) {
    width: 100%;
    align-items: center;
    display: flex;
    justify-content: flex-start;
}



</style>
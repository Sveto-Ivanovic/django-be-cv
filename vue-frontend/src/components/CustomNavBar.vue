<template>
    <div class="menu-wrapper">
        <div class="custom-menu-component">
            <div v-for="item in items" :key="item.label" :class="{ 'selected-menu': isActive === item.routeName }">
                <RouterLink class="router-link-custom" v-if="item.routeName" :to="{ name: item.routeName }">
                    <div class="menu-item-wrapper">
                        {{ item.label }}
                    </div>
                </RouterLink>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">

import { ref, watchEffect } from "vue";
import { RouterLink, useRoute } from 'vue-router'

const items = ref([
    {
        label: 'Home',
        routeName: 'Home',
        menuId: 'home-menu-id'
    },
    {
        label: 'About',
        routeName: 'About',
        menuId: 'about-menu-id'
    },
    {
        label: 'Contact',
        routeName: 'Contact',
        menuId: 'contact-menu-id'
    },
    {
        label: 'Log In',
        routeName: 'Login',
        menuId: 'login-menu-id'
    },

]);

let route = useRoute()
let isActive = ref<string>("")


watchEffect(() => {
    if (route.name) {
        let filtered_list = items.value.filter((item) => item.routeName == route.name)
        isActive.value = filtered_list[0].routeName
    }
})


</script>

<style scoped>
.menu-wrapper {
    position: fixed;
    top: 16px;
    left: 0;
    z-index: 100;
    display: flex;
    width: 100%;
    justify-content: center;
}

.custom-menu-component {
    background: var(--surface-color);
    backdrop-filter: blur(12px);
    display: flex;
    border: 1px solid var(--border-color-menu);
    border-radius: 20px;
    width: 60%;
    justify-content: space-around;
    padding: 6px;
    box-shadow:
        0 10px 30px rgba(0, 0, 0, 0.08);
}

.menu-item-wrapper {
    padding: 10px 16px;
    color: var(--text-color);
    font-size: 20px;
    border-radius: 14px;
    border: 1px solid transparent;
    transition:
        background .25s ease,
        transform .2s ease;
}

.menu-item-wrapper:hover {
    background: var(--menu-item-hover-color);
    transform: translateY(-2px);
}

.router-link-custom {
    text-decoration: none;
}

.selected-menu .menu-item-wrapper {
    background: var(--menu-item-hover-color);
    color: var(--accent-color);
    font-weight: 700;
}

@media(max-width:768px) {
    .menu-wrapper {
        position: fixed;
        bottom: 16px;
        left: 0;
        z-index: 100;
        top:auto;
    }

    .custom-menu-component {
        width: 90%;
        border-radius: 24px;
        padding: 8px;
        justify-content: space-evenly;
    }

    .menu-item-wrapper {
        padding: 10px 12px;
        font-size: 16px;
        border-radius: 16px;
    }

}
</style>

import { createPinia } from 'pinia'
import App from './App.vue'
import { routes } from './router'
import { setRouterInstance } from './router/router_instance.js'
import './assets/base.css'
import VueApexCharts from "vue3-apexcharts";
import { VueQueryPlugin } from '@tanstack/vue-query'
import naive from 'naive-ui'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import { ViteSSG } from 'vite-ssg'
import { useUserStore } from './stores/user_store/index.js'

export const createApp = ViteSSG(
    App,
    { routes },
    ({ app, router, initialState }) => {
        let isClient = !import.meta.env.SSR

        const pinia = createPinia()
        if (isClient) {
            pinia.use(piniaPluginPersistedstate)
        }
        app.use(pinia)
        app.use(VueQueryPlugin)
        app.use(naive)
        if (isClient) {
            app.use(VueApexCharts)
        }

        if (isClient) {
            setRouterInstance(router)
        }

        if (isClient) {
            router.beforeEach((to) => {
                const userStore = useUserStore()
                const isAuthenticated = userStore.isAuthenticated;
                const publicPages = ['Login', 'Register', 'Home', 'About', 'Contact', 'Missing', 'NotFound', 'ConfirmEmail'];

                document.title = to.meta.title || 'Testora';

                let descriptionTag = document.querySelector('meta[name="description"]');
                if (!descriptionTag) {
                    descriptionTag = document.createElement('meta');
                    descriptionTag.setAttribute('name', 'description');
                    document.head.appendChild(descriptionTag);
                }
                descriptionTag.setAttribute('content', to.meta.description || 'Build, Evaluate, and Compare AI Systems with Your Own Infrastructure.');

                if (publicPages.includes(to.name as string)) {
                    return true;
                }

                if (!isAuthenticated) {
                    return { name: 'Login' };
                }
            })
        }
    }
)

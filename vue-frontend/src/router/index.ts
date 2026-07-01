import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/Home.vue'
import { useUserStore } from '../stores/user_store/index.js';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: HomePage,
    },
    {
      path: '/about',
      name: 'About',
      component: () => import('../views/About.vue'),
    },
    {
      path: '/contact',
      name: 'Contact',
      component: () => import('../views/Contact.vue')
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue')
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/Register.vue')
    },
    {
      path: '/auth',
      name: 'Auth',
      component: () => import('../views/AuthPage.vue')
    },
    {
      path: '/missing',
      name: 'Missing',
      component: () => import('../views/MissingPage.vue')
    },

    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/MissingPage.vue')
    }
  ],
})


router.beforeEach((to, from) => {
  const userStore = useUserStore();
  const isAuthenticated = userStore.isAuthenticated;
  const publicPages = ['Login', 'Register', 'Home', 'About', 'Contact', 'Missing', 'NotFound'];

  if (publicPages.includes(to.name as string)) {
    return true;
  }

  if (!isAuthenticated) {
    return { name: 'Login' };
  }
})


export default router

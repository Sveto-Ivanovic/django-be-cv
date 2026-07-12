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
      path: '/testcases',
      name: 'TestCaseResults',
      component: () => import('../views/TestCasePages/TestCaseResults.vue')
    },
        {
      path: '/create-testcase',
      name: 'TestCaseCreate',
      component: () => import('../views/TestCasePages/TestCaseCreate.vue')
    },
        {
      path: '/testcase-statistics/:id',
      name: 'TestCaseResultStatistics',
      component: () => import('../views/TestCasePages/TestCaseResultStatistics.vue')
    },

    {
      path: '/supabase/supabase-namespaces',
      name: 'SupabaseNameSpaces',
      component: () => import('../views/SupabaseNamespacesViews/SupabaseNamespace.vue')
    },
    {
      path: '/supabase/supabase-embed',
      name: 'SupabaseEmbed',
      component: () => import('../views/SupabaseNamespacesViews/SupabaseEmbed.vue')
    },
    {
      path: '/supabase/supabase-namespaces/:namespace/:table_name',
      name: 'SupabaseNamespaceRecords',
      component: () => import('../views/SupabaseNamespacesViews/SupabaseNamespaceData.vue')
    },
    {
      path: '/pinecone/pinecone-embed',
      name: 'PineconeEmbed',
      component: () => import('../views/PineconeIndexViews/PineconeEmbed.vue')
    },

    {
      path: '/pinecone/pinecone-indexes',
      name: 'PineconeIndexes',
      component: () => import('../views/PineconeIndexViews/PineconeIndexes.vue')
    },
    {
      path: '/pinecone/pinecone-indexes/:index_name',
      name: 'PineconeIndexRecords',
      component: () => import('../views/PineconeIndexViews/PineconeIndexRecords.vue')
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/Dashboard.vue')
    },

    {
      path: '/profile',
      name: 'Profile',
      component: () => import('../views/Profile.vue')
    },

    {
      path: '/confirm-email',
      name: 'ConfirmEmail',
      component: () => import('../views/ConfirmEmail.vue')
    },
    {
      path: '/test',
      name: 'TestComponent',
      component: () => import('../views/TestComponentPage.vue')
    },
        {
      path: '/chatbot',
      name: 'ChatbotPage',
      component: () => import('../views/Chatbot.vue')
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
  const publicPages = ['Login', 'TestComponent', 'Register', 'Home', 'About', 'Contact', 'Missing', 'NotFound', 'ConfirmEmail'];

  if (publicPages.includes(to.name as string)) {
    return true;
  }

  if (!isAuthenticated) {
    return { name: 'Login' };
  }
})


export default router

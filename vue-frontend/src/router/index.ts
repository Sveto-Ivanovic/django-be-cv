import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/Home.vue'
import { useUserStore } from '../stores/user_store/index.js';
import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    description?: string
  }
}

export const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: {
      title: 'Testora',
      description: 'Build, Evaluate, and Compare AI Systems with Your Own Infrastructure.',
    },
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue'),
    meta: {
      title: 'About Testora',
      description: 'Learn more about Testora, a project exploring AI infrastructure, model evaluation, and performance measurement.',
    },
  },
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('../views/Contact.vue'),
    meta: {
      title: 'Contact Testora',
      description: 'Get in touch with the Testora team for inquiries, feedback, or support regarding our AI evaluation platform.',
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: {
      title: 'Logi In To Testora',
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: {
      title: 'Register To Testora',
    },
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
    path: '/chatbot',
    name: 'ChatbotPage',
    component: () => import('../views/Chatbot.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/MissingPage.vue')
  }
]

/*
// removed because i want home contact and about prerendered for optimized SOO
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, from) => {
  const userStore = useUserStore();
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

export default router

*/
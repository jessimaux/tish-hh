import { createRouter, createWebHistory } from '@ionic/vue-router';
import { RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import LoginPage from '@/views/LoginPage.vue';
import HomePage from '@/views/HomePage.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
    meta: {
      requiresAuth: true,
    }
  },
  {
    path: '/login/',
    name: 'login',
    component: LoginPage
  },

  // otherwise redirect to home
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const userIsAuthenticated = Boolean(localStorage.getItem('accessToken'))
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (userIsAuthenticated) {
      next()
    } else next('login')
  } 
  else if (userIsAuthenticated && (to.name == 'login' || to.name == 'register')) {
    next('/')
  } 
  else next()
})

export default router

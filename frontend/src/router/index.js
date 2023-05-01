import { createRouter, createWebHistory } from 'vue-router'

// TODO: split on many file
const routes = [
  // AUTH
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/login/',
    name: 'login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/register/',
    name: 'register',
    component: () => import('@/views/Register.vue')
  },
  {
    path: '/reset-password/',
    name: 'reset-password',
    component: () => import('@/views/ResetPassword.vue')
  },

  // PROFILE
  {
    path: '/profile/',
    name: 'profile',
    component: () => import('@/views/Profile.vue')
  },

  // FEED
  {
    path: '/feed/',
    name: 'feed',
    component: () => import('@/views/Feed.vue')
  },

  // BROWSE
  {
    path: '/browse/',
    name: 'browse',
    component: () => import('@/views/Browse.vue')
  },

  // otherwise redirect to home
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
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

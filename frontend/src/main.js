import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import 'bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css'

import '@/assets/css/style.css'
import { useAuthStore } from '@/stores/auth.js'

startApp()

async function startApp() {
  const app = createApp(App)

  app.use(createPinia())
  app.use(router)

  // attempt to auto refresh token before startup
  try {
    const authStore = useAuthStore()
    await authStore.refreshToken()
    await authStore.getCurrentUser()
  } catch {
    // catch error to start app on success or failure
  }

  router.isReady().then(() => {
    app.mount('#app')
  })
}

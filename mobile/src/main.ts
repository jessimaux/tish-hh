import { createApp } from 'vue'
import App from './App.vue'
import router from './router';

import { createPinia } from 'pinia'
import { useAuthStore } from './stores/auth';

import { IonicVue } from '@ionic/vue';

/* Core CSS required for Ionic components to work properly */
import '@ionic/vue/css/core.css';

/* Basic CSS for apps built with Ionic */
import '@ionic/vue/css/normalize.css';
import '@ionic/vue/css/structure.css';
import '@ionic/vue/css/typography.css';

/* Optional CSS utils that can be commented out */
import '@ionic/vue/css/padding.css';
import '@ionic/vue/css/float-elements.css';
import '@ionic/vue/css/text-alignment.css';
import '@ionic/vue/css/text-transformation.css';
import '@ionic/vue/css/flex-utils.css';
import '@ionic/vue/css/display.css';

/* Theme variables */
import './theme/variables.css';

/* Custom css */
import './assets/styles/style.css';

startApp();

// async start function to enable waiting for refresh token call
async function startApp() {
  const pinia = createPinia()

  const app = createApp(App)
    .use(IonicVue)
    .use(pinia)
    .use(router);

  // attempt to auto refresh token before startup
  try {
    const authStore = useAuthStore();
    await authStore.refreshToken();
  } catch {
    // catch error to start app on success or failure
  }

  app.mount('#app');
}
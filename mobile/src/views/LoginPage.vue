<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <div class="container">
        <div class="logo">
          <img class="logo" src="@/assets/images/logo/512w/logo.png">
        </div>

        <div class="authorization">
          <div class="ion-item-wrapper">
            <ion-item lines="none">
              <ion-input class='base' placeholder="Username or email" v-model="username"></ion-input>
            </ion-item>
          </div>
          <div class="ion-item-wrapper">
            <ion-item lines="none">
              <ion-input class='base' type="password" placeholder="Password" v-model="password"></ion-input>
            </ion-item>
            <router-link class="helper" :to="{ name: 'reset-password' }">Forgot your password?</router-link>
          </div>
        </div>

        <div class="footer">
          <ion-button type="submit" shape="round" fill="outline" @click="onSubmit">Login</ion-button>
          <div class="text-botoom">
            <p>Don't have an account? <router-link :to="{ name: 'register' }">Sign up</router-link></p>
          </div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { IonContent, IonPage, IonItem, IonInput, IonButton } from '@ionic/vue';
import { useAuthStore } from '@/stores/auth';

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')

async function onSubmit() {
  if (!!username.value.trim() && !!password.value.trim()) {
    const form = new FormData()
    form.append('username', username.value)
    form.append('password', password.value)
    await authStore.login(form)
      .then(() => {
        router.push({ name: 'home' })
      })
  }
}
</script>

<style lang="css" scoped src="@/assets/styles/login.css">

</style>

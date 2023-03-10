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
              <ion-input class='base' placeholder="Username or email" v-model="login" required></ion-input>
            </ion-item>
            <p class="errors">{{ errors.username }}</p>
          </div>
        </div>

        <div class="footer">
          <ion-button shape="round" fill="outline" :disabled="!meta.valid" @click="onSubmit">Reset</ion-button>
        </div>

      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { IonContent, IonPage, IonItem, IonInput, IonButton } from '@ionic/vue';
import { useRouter } from 'vue-router';
import { useField, useForm } from 'vee-validate';
import * as yup from 'yup';

import { useAuthStore } from '@/stores/auth';

const schema = yup.object({
  login: yup.string().required(),
});

const authStore = useAuthStore()
const router = useRouter()

const { errors, meta } = useForm({ validationSchema: schema })
const { value: login } = useField<string>('login')

async function onSubmit() {
  await authStore.retrievePassword(login.value)
  .then(() => {
    router.push({ name: 'login' })
  })
}
</script>

<style lang="css" scoped src="@/assets/styles/login.css">
</style>

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
              <ion-input class='base' placeholder="Username" v-model="username"></ion-input>
            </ion-item>
            <p class="errors">{{ errors.username }}</p>
          </div>
          <div class="ion-item-wrapper">
            <ion-item lines="none">
              <ion-input class='base' placeholder="Email" v-model="email"></ion-input>
            </ion-item>
            <p class="errors">{{ errors.email }}</p>
          </div>
          <div class="ion-item-wrapper">
            <ion-item lines="none">
              <ion-input class='base' type="password" placeholder="Password" v-model="password"></ion-input>
            </ion-item>
            <p class="errors">{{ errors.password }}</p>
          </div>
          <div class="ion-item-wrapper">
            <ion-item lines="none">
              <ion-input class='base' type="password" placeholder="Confirm password"
                v-model="confirmPassword"></ion-input>
            </ion-item>
            <p class="errors">{{ errors.confirmPassword }}</p>
          </div>
        </div>

        <div class="footer">
          <ion-button type="submit" shape="round" fill="outline" :disabled="!meta.valid" @click="onSubmit">Sign
            Up</ion-button>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { IonContent, IonPage, IonItem, IonInput, IonButton } from '@ionic/vue';
import { useField, useForm } from 'vee-validate';
import * as yup from 'yup';

import { useAuthStore } from '@/stores/auth';

const schema = yup.object({
  username: yup.string().required(),
  email: yup.string().required().email(),
  password: yup.string().required().min(8),
  confirmPassword: yup
    .string()
    .required()
    .oneOf([yup.ref('password')], 'Passwords must match')
});

const router = useRouter()
const authStore = useAuthStore()

const { errors, meta } = useForm({ validationSchema: schema })
const { value: username } = useField<string>('username')
const { value: email } = useField<string>('email')
const { value: password } = useField<string>('password')
const { value: confirmPassword } = useField<string>('confirmPassword')

async function onSubmit() {
  await authStore.registration(email.value, username.value, password.value)
    .then(() => {
      router.push({ name: 'login' })
    })
}
</script>

<style scoped>
@import '@/assets/styles/login.css';
</style>

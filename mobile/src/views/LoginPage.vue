<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <div id="container">
        <ion-label position="stacked">Login</ion-label>
        <ion-input placeholder="Username or email" v-model="user.username" required></ion-input>

        <ion-label position="stacked">Password</ion-label>
        <ion-input type="password" placeholder="Password" v-model="user.password" required></ion-input>

        <ion-button @click="onSubmit">Login</ion-button>
      </div>
    </ion-content>
  </ion-page>
</template>

<script lang="ts">
import { useRouter } from 'vue-router';
import { defineComponent } from 'vue';
import {
  IonContent, IonPage, IonInput, IonLabel, IonButton,
} from '@ionic/vue';
import { useAuthStore } from '@/stores/auth';

export default defineComponent({
  name: 'LoginPage',
  components: {
    IonContent,
    IonPage,
    IonInput,
    IonLabel,
    IonButton,
  },
  setup() {
    return {
      // router: useRouter(),
      authStore: useAuthStore()
    }
  },
  data() {
    return {
      user: {
        username: '',
        password: '',
      }
    }
  },
  methods: {
    onSubmit(){
      const form = new FormData()
      form.append('username', this.user.username)
      form.append('password', this.user.password)
      this.authStore.login(form)
      .then(()=>{
        this.$router.push({ name: 'home'})
      })
    }
  }
});
</script>

<style scoped>
#container {
  text-align: center;
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
}
</style>

<template>
  <ion-modal
    ref="modal-settings"
    trigger="open-modal-settings"
    :initial-breakpoint="0.25"
    :breakpoints="[0, 0.25, 0.5, 0.75]"
  >
    <ion-content class="ion-padding">
      <ion-list>
        <ion-item lines="none" button @click="logoutEvent">
          <ion-label>Logout</ion-label>
        </ion-item>
      </ion-list>
    </ion-content>
  </ion-modal>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { IonContent, IonLabel, IonItem, IonList, IonModal } from '@ionic/vue'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

function logoutEvent() {
  authStore.logout().then(() => {
    router.push({ name: 'login' })
  })
}
</script>

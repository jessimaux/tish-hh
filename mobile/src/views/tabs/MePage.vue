<template>
  <ion-page v-if="!userStore.isLoading">
    <ion-header class="ion-no-border">
      <ion-toolbar>
        <div class="toolbar-wrapper">
          <div class="semi-bold">{{ userStore.userData!.username }}</div>
          <ion-icon id="open-modal-settings" :icon="settingsOutline" />
        </div>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding profile">
      <tish-profile-base :user="userStore.userData!"></tish-profile-base>
      <tish-profile-options :self="true"></tish-profile-options>

      <ion-segment v-model="selectedSegment" value="all">
        <ion-segment-button value="all">
          <ion-icon :icon="gridOutline" />
        </ion-segment-button>
        <ion-segment-button value="creator">
          <ion-icon :icon="createOutline" />
        </ion-segment-button>
        <ion-segment-button value="member">
          <ion-icon :icon="peopleOutline" />
        </ion-segment-button>
      </ion-segment>
      <tish-profile-segment :selected="selectedSegment"></tish-profile-segment>
      <tish-modal-options></tish-modal-options>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  IonHeader,
  IonToolbar,
  IonContent,
  IonPage,
  IonIcon,
  IonSegment,
  IonSegmentButton,
} from '@ionic/vue'
import { gridOutline, peopleOutline, createOutline, settingsOutline } from 'ionicons/icons'

import { useUsersStore } from '@/stores/users'
import { useAuthStore } from '@/stores/auth'
import TishModalOptions from '@/components/general/TishModalOption.vue'
import TishProfileBase from '@/components/profile/TishProfileBase.vue'
import TishProfileOptions from '@/components/profile/TishProfileOptions.vue'
import TishProfileSegment from '@/components/profile/TishProfileSegment.vue'

const authStore = useAuthStore()
const userStore = useUsersStore()

onMounted(() => {
  userStore.getUser(authStore.currentUser!.username)
  userStore.getUserEvents(authStore.currentUser!.username, 'creator')
})

const selectedSegment = ref('all')
</script>

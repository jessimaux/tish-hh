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

    <ion-content>
      <div class="profile">
        <tish-profile-base :user="userStore.userData!"></tish-profile-base>
        
        <div class="options-section">
          <div class="item">
            <ion-button fill="outline" expand="block">Edit profile</ion-button>
          </div>
          <div class="item">
            <ion-button fill="outline" expand="block">Share profile</ion-button>
          </div>
        </div>

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

        <ion-grid v-if="selectedSegment === 'all'">
          <ion-row>
            <ion-col size="4">
              <img
                src="https://images.unsplash.com/photo-1484186139897-d5fc6b908812?ixlib=rb-0.3.5&amp;s=9358d797b2e1370884aa51b0ab94f706&amp;auto=format&amp;fit=crop&amp;w=200&amp;q=80%20500w"
              />
            </ion-col>
            <ion-col size="4">
              <img
                src="https://images.unsplash.com/photo-1484186139897-d5fc6b908812?ixlib=rb-0.3.5&amp;s=9358d797b2e1370884aa51b0ab94f706&amp;auto=format&amp;fit=crop&amp;w=200&amp;q=80%20500w"
              />
            </ion-col>
            <ion-col size="4">
              <img
                src="https://images.unsplash.com/photo-1484186139897-d5fc6b908812?ixlib=rb-0.3.5&amp;s=9358d797b2e1370884aa51b0ab94f706&amp;auto=format&amp;fit=crop&amp;w=200&amp;q=80%20500w"
              />
            </ion-col>
          </ion-row>
        </ion-grid>
      </div>
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
  IonButton,
  IonGrid,
  IonCol,
  IonRow
} from '@ionic/vue'
import { gridOutline, peopleOutline, createOutline, settingsOutline } from 'ionicons/icons'

import { useUsersStore } from '@/stores/users'
import { useAuthStore } from '@/stores/auth'

import tishModalOptions from '@/components/general/TishModalOption.vue'
import tishProfileBase from '@/components/profile/TishProfileBase.vue'

const authStore = useAuthStore()
const userStore = useUsersStore()

onMounted(() => {
  userStore.getUser(authStore.currentUser!.username)
  userStore.getUserEvents(authStore.currentUser!.username, 'creator')
})

const selectedSegment = ref('all')
</script>

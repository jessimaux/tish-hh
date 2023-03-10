<template>
  <ion-page>
    <ion-tabs>
      <ion-router-outlet></ion-router-outlet>
      <ion-tab-bar slot="bottom">
        <ion-tab-button tab="feed" href="/feed/">
          <ion-icon :icon="ticketOutline" />
          <ion-label>Feed</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="explore" href="/explore/">
          <ion-icon :icon="compassOutline" />
          <ion-label>Explore</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="add" href="#">
          <ion-icon :icon="addCircleOutline" size="large" />
        </ion-tab-button>

        <ion-tab-button tab="search" href="/search/">
          <ion-icon :icon="searchCircleOutline" />
          <ion-label>Search</ion-label>
        </ion-tab-button>
        
        <ion-tab-button tab="me" href="/me/">
          <ion-icon :icon="personOutline" />
          <ion-label>Me</ion-label>
        </ion-tab-button>
      </ion-tab-bar>
    </ion-tabs>
  </ion-page>
</template>

<script setup lang="ts">
import { IonTabBar, IonTabButton, IonTabs, IonLabel, IonIcon, IonPage, IonRouterOutlet } from '@ionic/vue';
import { compassOutline, searchCircleOutline, ticketOutline, addCircleOutline, personOutline } from 'ionicons/icons';
</script>
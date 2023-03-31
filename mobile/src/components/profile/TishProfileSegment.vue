<template>
  <ion-grid v-if="selected === 'all'">
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
</template>

<script setup lang="ts">
import { IonGrid, IonCol, IonRow } from '@ionic/vue'

const props = defineProps<{
  selected: string
}>()
</script>

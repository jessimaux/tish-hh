<template>
  <div class="options-section">
    <ion-button fill="outline" class="item" v-if="self">Edit profile</ion-button>
    <ion-button fill="outline" class="item" v-if="self">Share profile</ion-button>
    <ion-button fill="outline" class="item" v-if="!self">Follow</ion-button>
    <ion-button fill="outline" class="item" v-if="!self">Message</ion-button>
  </div>
</template>

<script setup lang="ts">
import { IonButton } from '@ionic/vue'

const props = defineProps<{
  self: boolean
}>()
</script>

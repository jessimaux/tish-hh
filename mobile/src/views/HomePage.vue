<template>
  <ion-page>
    {{ authStore.currentUser }}
  </ion-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { IonPage } from '@ionic/vue';
import { useAuthStore } from '@/stores/auth';

export default defineComponent({
  name: 'HomePage',
  components: {
    IonPage,
  },
  setup() {
    return {
      authStore: useAuthStore()
    }
  },
  mounted() {
    this.authStore.getCurrentUser()
  }
})
</script>

<style scoped>

</style>

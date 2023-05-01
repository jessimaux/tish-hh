<template>
  <div class="container">
    <navbar v-if="globalStore.showNavbar"></navbar>
    <main>
      <RouterView />
    </main>
    
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import Navbar from './components/general/Navbar.vue';
import {useGlobalStore} from '@/stores/global'

const globalStore = useGlobalStore()
</script>
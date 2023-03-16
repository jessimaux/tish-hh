<template>
  <div class="links-wrapper">
    <div v-for="link in links" :key="link.id" class="link">
      <a :href="link.link">{{ link.name }}</a>
    </div>
  </div>
</template>

<script></script>

<script setup lang="ts">
import { defineProps } from 'vue'
import type { ProfileLink } from '@/stores/users'

defineProps<{
  links?: ProfileLink[]
}>()
</script>

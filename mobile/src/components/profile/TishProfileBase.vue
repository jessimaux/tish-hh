<template>
  <div class="card">
    <div class="information-section">
      <div class="profile-image">
        <img :src="getProfileImage" class="thumbnail" />
      </div>
      <div class="user">
        <p class="semi-bold">{{ user.name }}</p>
        <p class="bio">{{ user.bio }}</p>
        <p class="location">{{ user.country }} {{ user.region }} {{ user.city }}</p>
        <div class="links-wrapper">
          <div v-for="link in user.links" :key="link.id" class="link">
            <a :href="link.link">{{ link.name }}</a>
          </div>
        </div>
      </div>
    </div>

    <div class="statistics-section">
      <div class="item">
        <div class="header semi-bold">{{ user.events_count }}</div>
        <div class="bottom">Events</div>
      </div>

      <div class="item">
        <div class="header semi-bold">{{ user.followers_count }}</div>
        <div class="bottom">Followers</div>
      </div>

      <div class="item">
        <div class="header semi-bold">{{ user.following_count }}</div>
        <div class="bottom">Following</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { IonButton } from '@ionic/vue'

import type { UserBase } from '@/stores/users'

const props = defineProps<{
  user: UserBase
}>()

const getProfileImage = computed(() => {
  return props.user.image ? props.user.image : '/src/assets/images/user/default.png'
})
</script>

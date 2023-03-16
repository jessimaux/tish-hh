<template>
  <div class="card">
    <div class="information-section">
      <div class="general">
        <div class="profile-image">
          <img :src="getProfileImage" class="thumbnail" />
        </div>
        <div class="user">
          <div class="semi-bold">{{ user.name }}</div>
          <div class="bio">{{ user.bio }}</div>
          <div class="location">
            {{ user.country }} {{ user.region }}
            {{ user.city }}
          </div>
          <tish-profile-link :links="user.links"></tish-profile-link>
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
import { computed, defineProps } from 'vue'
import { IonButton } from '@ionic/vue'

import TishProfileLink from './TishProfileLink.vue'
import type { UserBase } from '@/stores/users'

const props = defineProps<{
  user: UserBase
}>()

const getProfileImage = computed(() => {
  return props.user.image ? props.user.image : '/src/assets/images/user/default.png'
})
</script>

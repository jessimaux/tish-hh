<template>
  <div class="profile-wrapper">
    <div v-if="usersStore.userData" class="row mb-4 profile-header">
      <div class="col-lg-4 d-flex align-items-center justify-content-center">
        <img src="@/assets/img/user-default.png" alt="" width="125" />
      </div>
      <div class="col-lg-8 d-flex flex-column justify-content-center">
        <div class="row">
          <div class="col-lg-12 fw-bold">{{ usersStore.userData.username }}</div>
        </div>
        <div class="row">
          <div class="col-lg-4">{{ usersStore.userData.events_count }} Events</div>
          <div class="col-lg-4">{{ usersStore.userData.followers_count }} Followers</div>
          <div class="col-lg-4">{{ usersStore.userData.following_count }} Following</div>
        </div>
      </div>
    </div>

    <div class="row g-0">
      <div class="col-lg-4 d-flex align-items-center justify-content-center">
        <img src="@/assets/img/event-default.png" alt="" width="256" />
      </div>
      <div class="col-lg-4 d-flex align-items-center justify-content-center">
        <img src="@/assets/img/event-default.png" alt="" width="256" />
      </div>
      <div class="col-lg-4 d-flex align-items-center justify-content-center">
        <img src="@/assets/img/event-default.png" alt="" width="256" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useUsersStore } from '@/stores/users'

const usersStore = useUsersStore()
const authStore = useAuthStore()

usersStore.getUser(authStore.currentUser.username)
usersStore.getUserEvents(authStore.currentUser.username, 'creator')
</script>

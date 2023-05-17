<template>
  <div class="profile-wrapper">
    <div v-if="usersStore.userData" class="row mb-4">
      <div class="col-lg-4 d-flex align-items-center justify-content-center">
        <img :src="getProfileImage" alt="" width="125" />
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

    <ul class="nav nav-pills justify-content-center mb-3" id="pills-tab" role="tablist">
      <li class="nav-item" role="presentation">
        <button
          class="nav-link active"
          id="pills-home-tab"
          data-bs-toggle="pill"
          data-bs-target="#pills-home"
          type="button"
          role="tab"
          aria-controls="pills-home"
          aria-selected="true">
          Creator
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button
          class="nav-link"
          id="pills-profile-tab"
          data-bs-toggle="pill"
          data-bs-target="#pills-profile"
          type="button"
          role="tab"
          aria-controls="pills-profile"
          aria-selected="false">
          Member
        </button>
      </li>
    </ul>

    <div class="tab-content" id="pills-tabContent">
      <div
        class="tab-pane fade show active"
        id="pills-home"
        role="tabpanel"
        aria-labelledby="pills-home-tab"
        tabindex="0">
        <div class="row g-0">
          <div
            v-for="event in usersStore.eventsData"
            :key="event.event_id"
            class="col-lg-4 d-flex align-items-center justify-content-center">
            <img src="@/assets/img/event-default.png" alt="" width="256" />
          </div>
        </div>
      </div>
      <div
        class="tab-pane fade"
        id="pills-profile"
        role="tabpanel"
        aria-labelledby="pills-profile-tab"
        tabindex="0">
        ...
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUsersStore } from '@/stores/users'

const usersStore = useUsersStore()
const authStore = useAuthStore()

usersStore.getUser(authStore.currentUser.username)
usersStore.getUserEvents(authStore.currentUser.username, 'creator')

const getProfileImage = computed(() => {
  return !usersStore.userData
    ? usersStore.userData.image
    : window.location.origin + '/src/assets/img/user-default.png'
})
</script>

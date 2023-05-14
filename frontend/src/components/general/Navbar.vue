<template>
  <header id="header">
    <div class="container-fluid d-flex justify-content-between align-items-center">
      <router-link :to="{ name: 'feed' }" class="logo">
        <img class="logo" src="@/assets/img/logo/logo-125.png" alt="" />
      </router-link>

      <nav id="navbar" class="navbar">
        <ul>
          <li><router-link :to="{ name: 'feed' }">Feed</router-link></li>
          <li><router-link :to="{ name: 'browse' }">Browse</router-link></li>
          <li>
            <form class="d-flex">
              <input class="form-control me-1" placeholder="Search" aria-label="Search" />
              <button class="btn btn-tish" type="submit">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="20"
                  fill="currentColor"
                  class="bi bi-search"
                  viewBox="0 2 16 16">
                  <path
                    d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z" />
                </svg>
              </button>
            </form>
          </li>
        </ul>
      </nav>

      <div v-if="authStore.currentUser" class="profile d-flex align-items-center">
        <div class="profile-name me-1">{{ authStore.currentUser.username }}</div>
        <router-link :to="{ name: 'profile' }">
          <img src="@/assets/img/user-default.png" alt="" width="40" />
        </router-link>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

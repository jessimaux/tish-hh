<template>
  <div class="d-flex align-items-center justify-content-center h-100">
    <form
      class="d-flex flex-column"
      @submit.prevent="onSubmit">
      <div class="mb-5">
        <img
          src="@/assets/img/logo.png"
          alt="" />
      </div>

      <div class="mb-3">
        <input
          class="form-control"
          placeholder="Username or email"
          v-model="username" />
      </div>

      <div class="mb-3 text-end">
        <input
          type="password"
          class="form-control"
          placeholder="Password"
          v-model="password" />
        <router-link
          class="form-text"
          :to="{ name: 'reset-password' }"
          >Forgot your password?</router-link
        >
      </div>

      <button class="btn btn-tish">Sign in</button>
      <router-link
        class="form-text text-center"
        :to="{ name: 'register' }"
        >Doesnt have account? Sign up!</router-link
      >
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')

async function onSubmit() {
  const form = new FormData()
  form.append('username', username.value)
  form.append('password', password.value)
  await authStore.login(form).then(() => {
    router.push({ name: 'home' })
  })
}
</script>

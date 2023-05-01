<template>
  <div class="d-flex align-items-center justify-content-center h-100">
    <form class="d-flex flex-column">
      <div class="mb-5">
        <img src="@/assets/img/logo/logo-250.png" alt="" />
      </div>

      <div class="mb-3">
        <input class="form-control" placeholder="Username or email" />
      </div>

      <button class="btn btn-tish">Reset</button>
      <div class="form-text text-center">
        <router-link class="text-center" :to="{ name: 'login' }">Sign in</router-link> or
        <router-link class="text-center" :to="{ name: 'register' }">sign up!</router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useField, useForm } from 'vee-validate'
import * as yup from 'yup'

import { useAuthStore } from '@/stores/auth'

const schema = yup.object({
  login: yup.string().required()
})

const authStore = useAuthStore()
const router = useRouter()

const { errors, meta } = useForm({ validationSchema: schema })
const { value: login } = useField('login')

async function onSubmit() {
  await authStore.retrievePassword(login.value).then(() => {
    router.push({ name: 'login' })
  })
}
</script>

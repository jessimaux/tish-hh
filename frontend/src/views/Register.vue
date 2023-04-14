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
          placeholder="Username"
          v-model="username" />
        <div
          v-if="errors.username"
          class="invalid">
          {{ errors.username }}
        </div>
      </div>

      <div class="mb-3">
        <input
          class="form-control"
          placeholder="Email"
          v-model="email" />
        <div
          v-if="errors.email"
          class="invalid">
          {{ errors.email }}
        </div>
      </div>

      <div class="mb-3">
        <input
          type="password"
          class="form-control"
          placeholder="Password"
          v-model="password" />
        <div
          v-if="errors.password"
          class="invalid">
          {{ errors.password }}
        </div>
      </div>

      <div class="mb-3">
        <input
          type="password"
          class="form-control"
          placeholder="Confirm password"
          v-model="confirmPassword" />
        <div
          v-if="errors.confirmPassword"
          class="invalid">
          {{ errors.confirmPassword }}
        </div>
      </div>

      <button class="btn btn-tish">Sign up</button>
      <router-link
        class="form-text text-center"
        :to="{ name: 'login' }"
        >Already have account? Sign in!</router-link
      >
    </form>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useField, useForm } from 'vee-validate'
import * as yup from 'yup'

import { useAuthStore } from '@/stores/auth'

const schema = yup.object({
  username: yup.string().required(),
  email: yup.string().required().email(),
  password: yup.string().required().min(8),
  confirmPassword: yup
    .string()
    .required()
    .oneOf([yup.ref('password')], 'Passwords must match')
})

const router = useRouter()
const authStore = useAuthStore()

const { errors, meta } = useForm({ validationSchema: schema })
const { value: username } = useField('username')
const { value: email } = useField('email')
const { value: password } = useField('password')
const { value: confirmPassword } = useField('confirmPassword')

async function onSubmit() {
  await authStore.registration(email.value, username.value, password.value).then(() => {
    router.push({ name: 'login' })
  })
}
</script>

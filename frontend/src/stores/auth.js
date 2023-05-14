import { defineStore } from 'pinia'

import authApi from '@/api/auth'
import { getCookie, setCookie, eraseCookie } from '@/tools/core'

export const useAuthStore = defineStore('auth', {
  state: () => {
    return {
      data: null,
      currentUser: null,
      refreshTokenTimeout: 0,
      isLoading: false,
      errors: null
    }
  },
  actions: {
    async getCurrentUser() {
      this.errors = null
      this.isLoading = true
      await authApi
        .getCurrentUser()
        .then((response) => {
          this.isLoading = false
          this.currentUser = response.data
        })
        .catch(() => {
          this.isLoading = false
          this.currentUser = null
        })
    },

    async login(user) {
      this.currentUser = null
      this.errors = null
      this.isLoading = true
      await authApi
        .login(user)
        .then(async (response) => {
          localStorage.setItem('refreshToken', response.data.refresh_token)
          setCookie('accessToken', response.data.access_token, 1000 * 60 * 15)
          await this.getCurrentUser()
          this.isLoading = false
        })
        .catch((result) => {
          this.errors = result.response.data
          this.isLoading = false
          throw result.response.data
        })
      this.startRefreshTokenTimer()
    },

    async logout() {
      this.currentUser = null
      localStorage.removeItem('refreshToken')
      eraseCookie('accessToken')
      this.stopRefreshTokenTimer()
    },

    async refreshToken() {
      this.errors = null
      this.isLoading = true
      const refreshToken = localStorage.getItem('refreshToken')
      await authApi
        .refresh(refreshToken)
        .then(async (response) => {
          localStorage.setItem('refreshToken', response.data.refresh_token)
          setCookie('accessToken', response.data.access_token, 1000 * 60 * 15)
          this.isLoading = false
        })
        .catch((result) => {
          localStorage.removeItem('refreshToken')
          eraseCookie('accessToken')
          this.errors = result.response.data
          this.isLoading = false
          throw result.response.data
        })
      this.startRefreshTokenTimer()
    },

    startRefreshTokenTimer() {
      // set a timeout to refresh the token a minute before it expires
      this.refreshTokenTimeout = setTimeout(
        this.refreshToken,
        import.meta.env.VITE_JWT_ACCESS_TOKEN_EXPIRE_MINUTES
      )
    },

    stopRefreshTokenTimer() {
      clearTimeout(this.refreshTokenTimeout)
    },

    async registration(email, username, password) {
      this.errors = null
      this.isLoading = true
      await authApi
        .registration(email, username, password)
        .then(() => {
          this.isLoading = false
        })
        .catch((result) => {
          this.errors = result.response.data
          this.isLoading = false
          throw result.response.data
        })
    },

    async retrievePassword(login) {
      this.errors = null
      this.isLoading = true
      await authApi
        .retrievePassword(login)
        .then(() => {
          this.isLoading = false
        })
        .catch((result) => {
          this.errors = result.response.data
          this.isLoading = false
          throw result.response.data
        })
    }
  }
})

import { defineStore } from 'pinia'
import profileApi from '@/api/profile'

export const useProfileStore = defineStore('profile', {
  state: () => {
    return {
      data: null,
      isLoading: true,
      errors: null
    }
  },
  actions: {
    async getCurrentUser() {
      this.errors = null
      this.isLoading = true
      await profileApi
        .getCurrentUser()
        .then((response) => {
          this.isLoading = false
          this.data = response.data
        })
        .catch(() => {
          this.isLoading = false
          this.data = null
        })
    },

    async updateCurrentUser(data) {
      this.errors = null
      this.isLoading = true
      await profileApi
        .updateCurrentUser(data)
        .then((response) => {
          this.isLoading = false
          this.data = response.data
        })
        .catch(() => {
          this.isLoading = false
          this.data = null
        })
    },
  }
})

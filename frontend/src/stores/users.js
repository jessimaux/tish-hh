import { defineStore } from 'pinia'
import usersApi from '@/api/users'

export const useUsersStore = defineStore('users', {
  state: () => {
    return {
      userData: null,
      eventsData: null,
      isLoading: true,
      errors: null
    }
  },
  actions: {
    async getUser(username) {
      this.userData = null
      this.errors = null
      this.isLoading = true
      await usersApi
        .getUser(username)
        .then((response) => {
          this.isLoading = false
          this.userData = response.data
        })
        .catch((result) => {
          this.isLoading = false
          this.errors = result.response.data
          throw result.response.data
        })
    },

    async getUserEvents(username, role) {
      this.eventsData = null
      this.errors = null
      this.isLoading = true
      await usersApi
        .getUserEvents(username, role)
        .then((response) => {
          this.isLoading = false
          this.eventsData = response.data
        })
        .catch((result) => {
          this.isLoading = false
          this.errors = result.response.data
          throw result.response.data
        })
    }
  }
})

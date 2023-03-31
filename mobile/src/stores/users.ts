import { defineStore } from 'pinia'
import usersApi from '@/api/users'
import type { UserBase } from '@/stores/interfaces'

interface UserState {
  userData: UserBase | null
  eventsData: object | null
  isLoading: boolean
  errors: object | null
}

export const useUsersStore = defineStore({
  id: 'users',
  state: (): UserState => ({
    userData: null,
    eventsData: null,
    isLoading: true,
    errors: null
  }),
  actions: {
    async getUser(username: string) {
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

    async getUserEvents(username: string, role: string) {
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

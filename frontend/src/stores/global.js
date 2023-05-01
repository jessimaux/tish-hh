import { defineStore } from 'pinia'

export const useGlobalStore = defineStore('global', {
  state: () => {
    return {
      showNavbar: true
    }
  },
  actions: {
  }
})

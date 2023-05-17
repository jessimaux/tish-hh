import axios from '@/api/axios'

const getCurrentUser = () => {
  return axios.get('users/me/')
}

const updateCurrentUser = (data) => {
  return axios.put('users/me/', data)
}

export default {
  getCurrentUser,
  updateCurrentUser
}

import axios from '@/api/axios'

const getCurrentUser = () => {
  return axios.get('users/me/')
}

const login = (user: object) => {
  return axios.post('auth/token/', user, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  })
}

const refresh = (refresh_token: string | undefined) => {
  return axios.post('auth/refresh/', { token: refresh_token })
}

export default {
  login,
  refresh,
  getCurrentUser,
}
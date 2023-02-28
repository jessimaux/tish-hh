import axios from '@/api/axios'


const login = (user: object) => {
  return axios.post('auth/token/', user, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  })
}

const getCurrentUser = () => {
  return axios.get('users/me/')
}

export default {
  login,
  getCurrentUser,
}
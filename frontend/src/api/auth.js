import axios from '@/api/axios'

// test it wo header
const login = (user) => {
  return axios.post('auth/token/', user, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

const refresh = (refresh_token) => {
  return axios.post('auth/refresh/', { token: refresh_token })
}

const registration = (email, username, password) => {
  return axios.post('auth/registration/', { email: email, username: username, password: password })
}

const retrievePassword = (login) => {
  return axios.post('auth/send_retrieve_password/', { login: login })
}

const getCurrentUser = () => {
  return axios.get('users/me/')
}

export default {
  login,
  refresh,
  registration,
  retrievePassword,
  getCurrentUser
}

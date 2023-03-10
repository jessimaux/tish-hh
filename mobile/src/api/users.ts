import axios from '@/api/axios'

const getUser = (username: string) => {
  return axios.get(`users/${username}/`)
}

export default {
  getUser,
}
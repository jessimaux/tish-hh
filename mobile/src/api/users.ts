import axios from '@/api/axios'

const getUser = (username: string) => {
  return axios.get(`users/${username}/`)
}

const getUserEvents = (username: string, role: string) => {
  return axios.get(`users/${username}/events/`, { params: { role: role } })
}

export default {
  getUser,
  getUserEvents
}
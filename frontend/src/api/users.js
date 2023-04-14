import axios from '@/api/axios'

const getUser = (username) => {
  return axios.get(`users/${username}/`)
}

const getUserEvents = (username, role) => {
  return axios.get(`users/${username}/events/`, { params: { role: role } })
}

export default {
  getUser,
  getUserEvents
}

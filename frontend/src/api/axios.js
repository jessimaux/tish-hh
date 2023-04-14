import axios from 'axios'
import { getCookie } from '@/tools/core'

axios.defaults.baseURL = import.meta.env.VITE_API_URL

axios.interceptors.request.use((config) => {
  const token = getCookie('accessToken')
  const authorizationToken = token ? `Bearer ${token}` : ''
  config.headers.Authorization = authorizationToken
  return config
})

export default axios

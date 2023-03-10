import axios from 'axios'


axios.defaults.baseURL = import.meta.env.VITE_API_URL

// middleware: add auth header
axios.interceptors.request.use((config) => {
    const token = localStorage.getItem('accessToken')
    const authorizationToken = token ? `Bearer ${token}` : ''
    config.headers.Authorization = authorizationToken
    return config
  })

export default axios
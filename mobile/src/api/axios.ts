import axios from 'axios'


axios.defaults.baseURL = process.env.VUE_APP_API_URL

// middleware: add auth header
axios.interceptors.request.use((config) => {
    const token = localStorage.getItem('accessToken')
    const authorizationToken = token ? `Bearer ${token}` : ''
    config.headers.Authorization = authorizationToken
    return config
  })

export default axios
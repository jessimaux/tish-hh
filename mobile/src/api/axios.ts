import axios from 'axios'


axios.defaults.baseURL = 'http://127.0.0.1:8000/'

// middleware: add auth header
axios.interceptors.request.use((config) => {
    const token = localStorage.getItem('accessToken')
    const authorizationToken = token ? `Bearer ${token}` : ''
    config.headers.Authorization = authorizationToken
    return config
  })

export default axios
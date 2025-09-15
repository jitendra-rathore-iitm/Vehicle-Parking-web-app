import axios from 'axios'
import router from '../router/index.js'

const api = axios.create({
    baseURL: "https://vehicle-parking-web-app-1.onrender.com/",
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Add response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response.status === 401 || error.response.status === 403) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_role')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default api;
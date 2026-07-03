import axios from 'axios'

export class ApiError extends Error {
  code: string
  details?: Array<{ field: string; message: string }>

  constructor(message: string, code: string, details?: Array<{ field: string; message: string }>) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.details = details
  }
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: unknown) => void
  reject: (reason?: unknown) => void
}> = []

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      const errorCode = error.response?.data?.error?.code
      const isTokenExpired = errorCode === 'TOKEN_EXPIRED' || errorCode === 'AUTHENTICATION_ERROR'

      if (isTokenExpired) {
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject })
          }).then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
        }

        originalRequest._retry = true
        isRefreshing = true

        try {
          const { data } = await axios.post(
            `${import.meta.env.VITE_API_BASE_URL}/auth/refresh`,
            {},
            { withCredentials: true }
          )
          localStorage.setItem('access_token', data.access_token)
          api.defaults.headers.common.Authorization = `Bearer ${data.access_token}`
          processQueue(null, data.access_token)
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`
          return api(originalRequest)
        } catch (refreshError) {
          processQueue(refreshError, null)
          localStorage.removeItem('access_token')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      }
    }

    // Extract error message from backend's nested error format
    const responseData = error.response?.data
    if (responseData?.error?.message) {
      const apiError = new ApiError(
        responseData.error.message,
        responseData.error.code || 'UNKNOWN_ERROR',
        responseData.error.details
      )
      return Promise.reject(apiError)
    }

    return Promise.reject(error)
  }
)

export default api

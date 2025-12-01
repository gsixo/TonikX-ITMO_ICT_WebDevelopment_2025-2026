import axios from 'axios'

const DEFAULT_BASE_URL = 'http://127.0.0.1:8000'
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || DEFAULT_BASE_URL

const AUTH_TOKEN_KEY = 'museum-auth-token'

const commonConfig = {
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
}

export const apiClient = axios.create({
  ...commonConfig,
  baseURL: `${API_BASE_URL}/api`,
})

export const authClient = axios.create({
  ...commonConfig,
  baseURL: `${API_BASE_URL}/api/auth`,
})

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token)
  } else {
    localStorage.removeItem(AUTH_TOKEN_KEY)
  }
  const headerValue = token ? `Token ${token}` : undefined
  ;[apiClient, authClient].forEach((client) => {
    if (headerValue) {
      client.defaults.headers.common.Authorization = headerValue
    } else {
      delete client.defaults.headers.common.Authorization
    }
  })
}

export function bootstrapAuthToken() {
  const token = localStorage.getItem(AUTH_TOKEN_KEY)
  if (token) {
    setAuthToken(token)
    return token
  }
  return null
}

bootstrapAuthToken()


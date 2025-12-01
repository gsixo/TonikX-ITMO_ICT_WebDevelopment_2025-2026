import { defineStore } from 'pinia'
import { authClient, setAuthToken, bootstrapAuthToken } from '@/services/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: bootstrapAuthToken(),
    user: null,
    loading: false,
    error: null,
    ready: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },
  actions: {
    async login({ username, password }) {
      this.loading = true
      this.error = null
      try {
        const { data } = await authClient.post('/token/login/', { username, password })
        this.token = data.auth_token
        setAuthToken(this.token)
        await this.fetchProfile()
      } catch (error) {
        this.error = error.response?.data?.detail || 'Не удалось выполнить вход'
        throw error
      } finally {
        this.loading = false
      }
    },
    async logout() {
      try {
        await authClient.post('/token/logout/', {})
      } catch (_) {
        // noop: токен мог исторически протухнуть
      } finally {
        this.token = null
        this.user = null
        this.ready = true
        setAuthToken(null)
      }
    },
    async register(payload) {
      this.loading = true
      this.error = null
      try {
        await authClient.post('/users/', payload)
      } catch (error) {
        this.error = error.response?.data || 'Ошибка регистрации'
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchProfile() {
      if (!this.token) {
        this.user = null
        this.ready = true
        return null
      }
      this.loading = true
      this.error = null
      try {
        const { data } = await authClient.get('/users/me/')
        this.user = data
        return data
      } catch (error) {
        this.error = error.response?.data || 'Не удалось загрузить профиль'
        this.token = null
        setAuthToken(null)
        throw error
      } finally {
        this.loading = false
        this.ready = true
      }
    },
    async ensureUserLoaded() {
      if (this.ready) {
        return
      }
      try {
        await this.fetchProfile()
      } catch (_) {
        // ошибки уже обработаны в fetchProfile
      }
    },
    async updateProfile(updates) {
      if (!this.token) return null
      this.loading = true
      try {
        const { data } = await authClient.patch('/users/me/', updates)
        this.user = data
        return data
      } finally {
        this.loading = false
      }
    },
    async changePassword(payload) {
      if (!this.token) return null
      return authClient.post('/users/set_password/', payload)
    },
  },
})


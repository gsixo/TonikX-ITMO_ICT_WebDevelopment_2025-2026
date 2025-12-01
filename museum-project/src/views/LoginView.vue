<script setup>
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
})
const errorMessage = ref('')

const handleSubmit = async () => {
  errorMessage.value = ''
  loading.value = true
  try {
    await auth.login(form)
    const redirect = route.query.next || { name: 'dashboard' }
    router.push(redirect)
  } catch (error) {
    errorMessage.value = auth.error || error.response?.data?.detail || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <v-container fluid class="py-12">
    <v-row justify="center">
      <v-col cols="12" md="5">
        <v-card elevation="4">
          <v-card-title class="text-h5">Вход в систему</v-card-title>
          <v-card-subtitle>Используйте учётные данные Django пользователя</v-card-subtitle>
          <v-divider></v-divider>
          <v-card-text>
            <v-alert
              v-if="errorMessage"
              type="error"
              class="mb-4"
              density="compact"
              border="start"
            >
              {{ errorMessage }}
            </v-alert>
            <v-form @submit.prevent="handleSubmit">
              <v-text-field
                v-model="form.username"
                label="Имя пользователя"
                prepend-inner-icon="mdi-account"
                required
                autocomplete="username"
              />
              <v-text-field
                v-model="form.password"
                label="Пароль"
                type="password"
                prepend-inner-icon="mdi-lock"
                required
                autocomplete="current-password"
              />
              <v-btn
                type="submit"
                :loading="loading"
                :disabled="loading"
                block
                color="primary"
                class="mt-4"
              >
                Войти
              </v-btn>
              <v-btn
                variant="text"
                block
                class="mt-2"
                :to="{ name: 'register' }"
              >
                Нет аккаунта? Зарегистрироваться
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>


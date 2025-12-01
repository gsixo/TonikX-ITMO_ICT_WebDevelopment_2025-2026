<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const loading = ref(false)
const success = ref(false)
const errors = ref({})
const form = reactive({
  username: '',
  email: '',
  password: '',
  re_password: '',
})

const handleSubmit = async () => {
  success.value = false
  errors.value = {}
  loading.value = true
  try {
    await auth.register(form)
    success.value = true
    setTimeout(() => {
      router.push({ name: 'login', query: { username: form.username } })
    }, 1500)
  } catch (error) {
    errors.value = error.response?.data || { detail: 'Регистрация не удалась' }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <v-container fluid class="py-12">
    <v-row justify="center">
      <v-col cols="12" md="6" lg="5">
        <v-card elevation="4">
          <v-card-title class="text-h5">Регистрация пользователя</v-card-title>
          <v-card-text>
            <v-alert
              v-if="success"
              type="success"
              class="mb-4"
              border="start"
              density="compact"
            >
              Аккаунт создан! Сейчас произойдёт перенаправление на страницу входа.
            </v-alert>
            <v-alert
              v-if="errors.detail"
              type="error"
              class="mb-4"
              border="start"
              density="compact"
            >
              {{ errors.detail }}
            </v-alert>
            <v-form @submit.prevent="handleSubmit">
              <v-text-field
                v-model="form.username"
                label="Имя пользователя"
                prepend-inner-icon="mdi-account"
                required
              />
              <v-text-field
                v-model="form.email"
                label="Email"
                prepend-inner-icon="mdi-email"
                type="email"
                required
              />
              <v-text-field
                v-model="form.password"
                label="Пароль"
                type="password"
                prepend-inner-icon="mdi-lock"
                required
              />
              <v-text-field
                v-model="form.re_password"
                label="Повторите пароль"
                type="password"
                prepend-inner-icon="mdi-lock-check"
                required
              />
              <div v-if="errors.password" class="text-error text-caption mb-2">
                {{ errors.password.join(', ') }}
              </div>
              <div v-if="errors.username" class="text-error text-caption mb-2">
                {{ errors.username.join(', ') }}
              </div>
              <v-btn
                type="submit"
                color="primary"
                block
                class="mt-4"
                :loading="loading"
              >
                Создать аккаунт
              </v-btn>
              <v-btn
                variant="text"
                block
                class="mt-2"
                :to="{ name: 'login' }"
              >
                Уже есть аккаунт? Войти
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>


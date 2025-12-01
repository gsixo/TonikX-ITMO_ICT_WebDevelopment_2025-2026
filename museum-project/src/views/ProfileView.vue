<script setup>
import { reactive, ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authClient } from '@/services/http'

const auth = useAuthStore()
const profileForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
})
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  re_new_password: '',
})
const profileLoading = ref(false)
const passwordLoading = ref(false)
const profileMessage = ref('')
const passwordMessage = ref('')
const passwordError = ref('')

watch(
  () => auth.user,
  (user) => {
    if (!user) return
    profileForm.username = user.username
    profileForm.email = user.email
    profileForm.first_name = user.first_name || ''
    profileForm.last_name = user.last_name || ''
  },
  { immediate: true }
)

const saveProfile = async () => {
  profileLoading.value = true
  profileMessage.value = ''
  try {
    await auth.updateProfile({
      email: profileForm.email,
      first_name: profileForm.first_name,
      last_name: profileForm.last_name,
    })
    profileMessage.value = 'Профиль обновлён'
  } finally {
    profileLoading.value = false
  }
}

const changePassword = async () => {
  passwordLoading.value = true
  passwordMessage.value = ''
  passwordError.value = ''
  try {
    await authClient.post('/users/set_password/', {
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
      re_new_password: passwordForm.re_new_password,
    })
    passwordMessage.value = 'Пароль изменён'
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.re_new_password = ''
  } catch (error) {
    passwordError.value =
      error.response?.data?.current_password?.join(', ') ||
      error.response?.data?.new_password?.join(', ') ||
      error.response?.data?.detail ||
      'Не удалось изменить пароль'
  } finally {
    passwordLoading.value = false
  }
}
</script>

<template>
  <v-container fluid class="py-6">
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Профиль</v-card-title>
          <v-card-subtitle>Основные учётные данные</v-card-subtitle>
          <v-card-text>
            <v-alert
              v-if="profileMessage"
              type="success"
              class="mb-4"
              density="compact"
              border="start"
            >
              {{ profileMessage }}
            </v-alert>
            <v-form @submit.prevent="saveProfile">
              <v-text-field
                v-model="profileForm.username"
                label="Имя пользователя"
                readonly
                prepend-inner-icon="mdi-account"
              />
              <v-text-field
                v-model="profileForm.email"
                label="Email"
                type="email"
                prepend-inner-icon="mdi-email"
                required
              />
              <v-text-field
                v-model="profileForm.first_name"
                label="Имя"
                prepend-inner-icon="mdi-account-box"
              />
              <v-text-field
                v-model="profileForm.last_name"
                label="Фамилия"
                prepend-inner-icon="mdi-account-box-outline"
              />
              <v-btn
                type="submit"
                color="primary"
                :loading="profileLoading"
              >
                Сохранить
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Смена пароля</v-card-title>
          <v-card-text>
            <v-alert
              v-if="passwordMessage"
              type="success"
              class="mb-4"
              density="compact"
              border="start"
            >
              {{ passwordMessage }}
            </v-alert>
            <v-alert
              v-if="passwordError"
              type="error"
              class="mb-4"
              density="compact"
              border="start"
            >
              {{ passwordError }}
            </v-alert>
            <v-form @submit.prevent="changePassword">
              <v-text-field
                v-model="passwordForm.current_password"
                label="Текущий пароль"
                type="password"
                prepend-inner-icon="mdi-lock"
                required
              />
              <v-text-field
                v-model="passwordForm.new_password"
                label="Новый пароль"
                type="password"
                prepend-inner-icon="mdi-lock-plus"
                required
              />
              <v-text-field
                v-model="passwordForm.re_new_password"
                label="Повторите новый пароль"
                type="password"
                prepend-inner-icon="mdi-lock-check"
                required
              />
              <v-btn
                type="submit"
                color="primary"
                :loading="passwordLoading"
              >
                Изменить пароль
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>


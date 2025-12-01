<script setup>
import { ref, computed, watch } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const drawer = ref(false)
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const navItems = [
  { title: 'Дашборд', icon: 'mdi-view-dashboard', to: { name: 'dashboard' }, requiresAuth: true },
  { title: 'Фонды', icon: 'mdi-warehouse', to: { name: 'funds' }, requiresAuth: true },
  { title: 'Комплекты', icon: 'mdi-layers', to: { name: 'collections' }, requiresAuth: true },
  { title: 'Предметы', icon: 'mdi-package-variant', to: { name: 'items' }, requiresAuth: true },
  { title: 'Авторы', icon: 'mdi-account-multiple', to: { name: 'authors' }, requiresAuth: true },
  { title: 'Движения', icon: 'mdi-swap-horizontal', to: { name: 'movement-acts' }, requiresAuth: true },
  { title: 'Отчёты', icon: 'mdi-chart-box', to: { name: 'reports' }, requiresAuth: true },
  { title: 'Профиль', icon: 'mdi-account-circle', to: { name: 'profile' }, requiresAuth: true },
]

const menuItems = computed(() =>
  navItems.filter((item) => (item.requiresAuth ? auth.isAuthenticated : true))
)

const toggleDrawer = () => {
  drawer.value = !drawer.value
}

const logout = async () => {
  await auth.logout()
  router.push({ name: 'login' })
}

watch(route, () => {
  drawer.value = false
})
</script>

<template>
  <v-app>
    <v-navigation-drawer
      v-model="drawer"
      app
      color="primary-darken-1"
      class="text-white"
    >
      <v-toolbar flat color="transparent">
        <v-icon class="mr-2">mdi-museum</v-icon>
        <v-toolbar-title>Музейный фонд</v-toolbar-title>
      </v-toolbar>
      <v-divider class="mb-3"></v-divider>
      <v-list density="comfortable" nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :to="item.to"
          prepend-icon=""
        >
          <template #prepend>
            <v-icon>{{ item.icon }}</v-icon>
          </template>
          {{ item.title }}
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar app color="primary" dark>
      <v-app-bar-nav-icon @click="toggleDrawer" />
      <v-toolbar-title>Информационная система музея</v-toolbar-title>
      <v-spacer />
      <div v-if="auth.isAuthenticated" class="d-flex align-center ga-4">
        <div class="text-body-2">
          {{ auth.user?.first_name || auth.user?.username }}
        </div>
        <v-btn variant="tonal" @click="logout">
          Выйти
        </v-btn>
      </div>
      <v-btn
        v-else
        variant="tonal"
        color="white"
        :to="{ name: 'login' }"
      >
        Войти
      </v-btn>
    </v-app-bar>

    <v-main>
      <RouterView />
    </v-main>
  </v-app>
</template>

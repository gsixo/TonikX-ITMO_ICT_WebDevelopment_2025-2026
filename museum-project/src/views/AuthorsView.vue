<script setup>
import { ref, reactive, onMounted } from 'vue'
import { apiClient } from '@/services/http'

const authors = ref([])
const loading = ref(false)
const dialog = ref(false)
const form = reactive({
  id: null,
  full_name: '',
  birth_date: '',
  country: '',
})

const headers = [
  { title: 'ФИО', key: 'full_name' },
  { title: 'Дата рождения', key: 'birth_date' },
  { title: 'Страна', key: 'country' },
  { title: 'Действия', key: 'actions', align: 'end', sortable: false },
]

const loadAuthors = async () => {
  loading.value = true
  try {
    const { data } = await apiClient.get('/authors/', { params: { page_size: 200 } })
    authors.value = data.results ?? data
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  form.id = null
  form.full_name = ''
  form.birth_date = ''
  form.country = ''
  dialog.value = true
}

const openEdit = (author) => {
  form.id = author.id
  form.full_name = author.full_name
  form.birth_date = author.birth_date
  form.country = author.country
  dialog.value = true
}

const saveAuthor = async () => {
  const payload = {
    full_name: form.full_name,
    birth_date: form.birth_date || null,
    country: form.country,
  }
  if (form.id) {
    await apiClient.patch(`/authors/${form.id}/`, payload)
  } else {
    await apiClient.post('/authors/', payload)
  }
  dialog.value = false
  await loadAuthors()
}

const deleteAuthor = async (author) => {
  if (!confirm(`Удалить автора "${author.full_name}"?`)) return
  await apiClient.delete(`/authors/${author.id}/`)
  await loadAuthors()
}

onMounted(loadAuthors)
</script>

<template>
  <v-container fluid class="py-6">
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <div>
          <div class="text-h5">Авторы</div>
          <div class="text-body-2 text-medium-emphasis">Создание и редактирование карточек авторов</div>
        </div>
        <v-btn color="primary" @click="openCreate">
          <v-icon class="mr-2">mdi-plus</v-icon>
          Добавить автора
        </v-btn>
      </v-card-title>
      <v-data-table
        :headers="headers"
        :items="authors"
        :loading="loading"
      >
        <template #item.actions="{ item }">
          <v-btn icon="mdi-pencil" size="small" variant="text" @click="openEdit(item)" />
          <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteAuthor(item)" />
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="dialog" max-width="500">
      <v-card>
        <v-card-title>{{ form.id ? 'Редактирование автора' : 'Новый автор' }}</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="saveAuthor">
            <v-text-field v-model="form.full_name" label="ФИО" required />
            <v-text-field v-model="form.birth_date" type="date" label="Дата рождения" />
            <v-text-field v-model="form.country" label="Страна" />
          </v-form>
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="dialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="saveAuthor">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>
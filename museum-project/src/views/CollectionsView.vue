<script setup>
import { ref, reactive, onMounted } from 'vue'
import { apiClient } from '@/services/http'

const collections = ref([])
const auxIndexes = ref([])
const funds = ref([])
const dialog = ref(false)
const loading = ref(false)
const indexDialog = ref(false)
const form = reactive({
  id: null,
  name: '',
  auxiliary_index_id: null,
})
const indexForm = reactive({
  name: '',
  fund_id: null,
  notes: '',
})

const headers = [
  { title: 'Название', key: 'name' },
  { title: 'Картотека', key: 'auxiliary_index.name' },
  { title: 'Фонд', key: 'auxiliary_index.fund.name' },
  { title: 'Предметов', key: 'items_count', align: 'end' },
  { title: 'Действия', key: 'actions', align: 'end', sortable: false },
]

const resetForm = () => {
  form.id = null
  form.name = ''
  form.auxiliary_index_id = null
}

const loadCollections = async () => {
  loading.value = true
  try {
    const { data } = await apiClient.get('/collections/', { params: { page_size: 200 } })
    collections.value = data.results ?? data
  } finally {
    loading.value = false
  }
}

const loadIndexes = async () => {
  const { data } = await apiClient.get('/auxiliary-indexes/', { params: { page_size: 200 } })
  auxIndexes.value = data.results ?? data
}

const loadFunds = async () => {
  const { data } = await apiClient.get('/funds/', { params: { page_size: 200 } })
  funds.value = data.results ?? data
}

const openCreate = () => {
  resetForm()
  dialog.value = true
}

const openEdit = (collection) => {
  form.id = collection.id
  form.name = collection.name
  form.auxiliary_index_id = collection.auxiliary_index || collection.auxiliary_index_id
  if (typeof form.auxiliary_index_id === 'object') {
    form.auxiliary_index_id = collection.auxiliary_index?.id
  }
  dialog.value = true
}

const saveCollection = async () => {
  const payload = {
    name: form.name,
    auxiliary_index_id: form.auxiliary_index_id,
  }
  if (form.id) {
    await apiClient.patch(`/collections/${form.id}/`, payload)
  } else {
    await apiClient.post('/collections/', payload)
  }
  dialog.value = false
  await loadCollections()
}

const deleteCollection = async (collection) => {
  if (!confirm(`Удалить комплект "${collection.name}"?`)) return
  await apiClient.delete(`/collections/${collection.id}/`)
  await loadCollections()
}

const saveIndex = async () => {
  await apiClient.post('/auxiliary-indexes/', {
    name: indexForm.name,
    fund: indexForm.fund_id,
    notes: indexForm.notes,
  })
  indexDialog.value = false
  indexForm.name = ''
  indexForm.fund_id = null
  indexForm.notes = ''
  await loadIndexes()
}

onMounted(async () => {
  await Promise.all([loadCollections(), loadIndexes(), loadFunds()])
})
</script>

<template>
  <v-container fluid class="py-6">
    <v-card class="mb-6">
      <v-card-title class="d-flex justify-space-between align-center">
        <div>
          <div class="text-h5">Комплекты (картотеки)</div>
          <div class="text-body-2 text-medium-emphasis">
            Управление наборами и вспомогательными картотеками
          </div>
        </div>
        <div class="d-flex ga-2">
          <v-btn variant="tonal" color="secondary" @click="indexDialog = true">
            Новая картотека
          </v-btn>
          <v-btn color="primary" @click="openCreate">
            <v-icon class="mr-2">mdi-plus</v-icon>
            Добавить комплект
          </v-btn>
        </div>
      </v-card-title>
      <v-data-table
        :headers="headers"
        :items="collections"
        :loading="loading"
        class="border-t"
      >
        <template #item['auxiliary_index.name']="{ item }">
          {{ item.auxiliary_index?.name || '—' }}
        </template>
        <template #item['auxiliary_index.fund.name']="{ item }">
          {{ item.auxiliary_index?.fund?.name || '—' }}
        </template>
        <template #item.actions="{ item }">
          <v-btn
            icon="mdi-pencil"
            size="small"
            variant="text"
            @click="openEdit(item)"
          />
          <v-btn
            icon="mdi-delete"
            size="small"
            variant="text"
            color="error"
            @click="deleteCollection(item)"
          />
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="dialog" max-width="500">
      <v-card>
        <v-card-title>
          {{ form.id ? 'Редактирование комплекта' : 'Новый комплект' }}
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="saveCollection">
            <v-text-field
              v-model="form.name"
              label="Название комплекта"
              required
            />
            <v-select
              v-model="form.auxiliary_index_id"
              :items="auxIndexes"
              item-title="name"
              item-value="id"
              label="Вспомогательная картотека"
              return-object="false"
              clearable
              hint="Опционально"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="dialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="saveCollection">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="indexDialog" max-width="500">
      <v-card>
        <v-card-title>Новая картотека</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="saveIndex">
            <v-text-field
              v-model="indexForm.name"
              label="Название"
              required
            />
            <v-select
              v-model="indexForm.fund_id"
              :items="funds"
              item-title="name"
              item-value="id"
              label="Фонд"
              required
            />
            <v-textarea
              v-model="indexForm.notes"
              label="Заметки"
              rows="3"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="indexDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="saveIndex">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>


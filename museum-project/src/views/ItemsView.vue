<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { apiClient } from '@/services/http'

const items = ref([])
const funds = ref([])
const authors = ref([])
const collections = ref([])
const search = ref('')
const selectedFund = ref(null)
const loading = ref(false)
const dialog = ref(false)
const authorDialog = ref(false)
const form = reactive({
  id: null,
  inventory_number: '',
  name: '',
  creation_date: '',
  creation_exact: true,
  fund_id: null,
  author_id: null,
  collection_id: null,
  notes: '',
})
const authorForm = reactive({
  full_name: '',
  birth_date: '',
  country: '',
})

const headers = [
  { title: 'Инв. №', key: 'inventory_number' },
  { title: 'Название', key: 'name' },
  { title: 'Фонд', key: 'fund.name' },
  { title: 'Автор', key: 'author.full_name' },
  { title: 'Коллекция', key: 'collection.name' },
  { title: 'Дата', key: 'creation_date' },
  { title: 'Списан', key: 'is_written_off', align: 'center' },
  { title: 'Действия', key: 'actions', align: 'end', sortable: false },
]

const filteredItems = computed(() => {
  return (items.value || [])
    .filter((item) =>
      !selectedFund.value ? true : item.fund?.id === selectedFund.value
    )
    .filter((item) =>
      item.name.toLowerCase().includes(search.value.toLowerCase()) ||
      item.inventory_number.toLowerCase().includes(search.value.toLowerCase())
    )
})

const resetForm = () => {
  form.id = null
  form.inventory_number = ''
  form.name = ''
  form.creation_date = ''
  form.creation_exact = true
  form.fund_id = null
  form.author_id = null
  form.collection_id = null
  form.notes = ''
}

const loadItems = async () => {
  loading.value = true
  try {
    const { data } = await apiClient.get('/items/', { params: { page_size: 200 } })
    items.value = data.results ?? data
  } finally {
    loading.value = false
  }
}

const loadLookups = async () => {
  const [fundsRes, authorsRes, collectionsRes] = await Promise.all([
    apiClient.get('/funds/', { params: { page_size: 200 } }),
    apiClient.get('/authors/', { params: { page_size: 200 } }),
    apiClient.get('/collections/', { params: { page_size: 200 } }),
  ])
  funds.value = fundsRes.data.results ?? fundsRes.data
  authors.value = authorsRes.data.results ?? authorsRes.data
  collections.value = collectionsRes.data.results ?? collectionsRes.data
}

const openCreate = () => {
  resetForm()
  dialog.value = true
}

const openEdit = (item) => {
  form.id = item.id
  form.inventory_number = item.inventory_number
  form.name = item.name
  form.creation_date = item.creation_date
  form.creation_exact = item.creation_exact
  form.fund_id = item.fund?.id || null
  form.author_id = item.author?.id || null
  form.collection_id = item.collection?.id || null
  form.notes = item.notes
  dialog.value = true
}

const ensureAuthor = async () => {
  if (!authorForm.full_name) return null
  const payload = {
    full_name: authorForm.full_name,
    birth_date: authorForm.birth_date || null,
    country: authorForm.country,
  }
  const { data } = await apiClient.post('/authors/', payload)
  await loadLookups()
  form.author_id = data.id
  authorDialog.value = false
  authorForm.full_name = ''
  authorForm.birth_date = ''
  authorForm.country = ''
  return data.id
}

const saveItem = async () => {
  const payload = {
    inventory_number: form.inventory_number,
    name: form.name,
    creation_date: form.creation_date || null,
    creation_exact: form.creation_exact,
    fund_id: form.fund_id,
    author_id: form.author_id,
    collection_id: form.collection_id,
    notes: form.notes,
  }
  if (form.id) {
    await apiClient.patch(`/items/${form.id}/`, payload)
  } else {
    await apiClient.post('/items/', payload)
  }
  dialog.value = false
  await loadItems()
}

const deleteItem = async (item) => {
  if (!confirm(`Удалить предмет "${item.name}"?`)) return
  await apiClient.delete(`/items/${item.id}/`)
  await loadItems()
}

onMounted(async () => {
  await Promise.all([loadItems(), loadLookups()])
})
</script>

<template>
  <v-container fluid class="py-6">
    <v-card>
      <v-card-title class="d-flex flex-column flex-sm-row justify-space-between align-center ga-4">
        <div>
          <div class="text-h5">Карточки музейных предметов</div>
          <div class="text-body-2 text-medium-emphasis">
            Создание, редактирование и фильтрация карточек
          </div>
        </div>
        <v-btn color="primary" @click="openCreate">
          <v-icon class="mr-2">mdi-plus</v-icon>
          Добавить предмет
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-row class="mb-4">
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search"
              label="Поиск по названию или инв. номеру"
              prepend-inner-icon="mdi-magnify"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedFund"
              :items="funds"
              item-title="name"
              item-value="id"
              label="Фильтр по фонду"
              clearable
            />
          </v-col>
        </v-row>
        <v-data-table
          :headers="headers"
          :items="filteredItems"
          :loading="loading"
          :items-per-page="10"
        >
          <template #item['fund.name']="{ item }">
            {{ item.fund?.name || '—' }}
          </template>
          <template #item['author.full_name']="{ item }">
            {{ item.author?.full_name || '—' }}
          </template>
          <template #item['collection.name']="{ item }">
            {{ item.collection?.name || '—' }}
          </template>
          <template #item.is_written_off="{ item }">
            <v-icon :color="item.is_written_off ? 'error' : 'success'">
              {{ item.is_written_off ? 'mdi-close-circle' : 'mdi-check-circle' }}
            </v-icon>
          </template>
          <template #item.actions="{ item }">
            <v-btn icon="mdi-pencil" size="small" variant="text" @click="openEdit(item)" />
            <v-btn
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
              @click="deleteItem(item)"
            />
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="dialog" max-width="700">
      <v-card>
        <v-card-title>
          {{ form.id ? 'Редактирование предмета' : 'Новый предмет' }}
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="saveItem">
            <v-text-field
              v-model="form.inventory_number"
              label="Инвентарный номер"
              required
            />
            <v-text-field
              v-model="form.name"
              label="Название"
              required
            />
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.creation_date"
                  label="Дата создания"
                  type="date"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-switch
                  v-model="form.creation_exact"
                  label="Дата определена точно"
                />
              </v-col>
            </v-row>
            <v-select
              v-model="form.fund_id"
              :items="funds"
              item-title="name"
              item-value="id"
              label="Фонд"
              required
            />
            <v-select
              v-model="form.author_id"
              :items="authors"
              item-title="full_name"
              item-value="id"
              label="Автор"
              clearable
              append-inner-icon="mdi-account-plus"
              @click:append-inner="authorDialog = true"
            />
            <v-select
              v-model="form.collection_id"
              :items="collections"
              item-title="name"
              item-value="id"
              label="Коллекция"
              clearable
            />
            <v-textarea
              v-model="form.notes"
              label="Заметки"
              rows="3"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="dialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="saveItem">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="authorDialog" max-width="500">
      <v-card>
        <v-card-title>Новый автор</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="ensureAuthor">
            <v-text-field
              v-model="authorForm.full_name"
              label="ФИО"
              required
            />
            <v-text-field
              v-model="authorForm.birth_date"
              label="Дата рождения"
              type="date"
            />
            <v-text-field
              v-model="authorForm.country"
              label="Страна"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="authorDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="ensureAuthor">Добавить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>


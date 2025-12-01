<script setup>
import { ref, reactive, onMounted } from 'vue'
import { apiClient } from '@/services/http'

const FUND_TYPES = [
  { value: 'painting', title: 'Живопись' },
  { value: 'graphics', title: 'Графика' },
  { value: 'icon', title: 'Икона' },
  { value: 'sculpture', title: 'Скульптура' },
  { value: 'dpa', title: 'ДПИ' },
  { value: 'numismatics', title: 'Нумизматика' },
  { value: 'archaeology', title: 'Археология' },
  { value: 'manuscripts', title: 'Рукописи' },
  { value: 'rare_book', title: 'Редкая книга' },
  { value: 'other', title: 'Другое' },
]

const funds = ref([])
const addresses = ref([])
const dialog = ref(false)
const isEdit = ref(false)
const loading = ref(false)
const form = reactive({
  id: null,
  name: '',
  fund_type: 'other',
  description: '',
  address_id: null,
  address_line: '',
})

const headers = [
  { title: 'Название', key: 'name' },
  { title: 'Тип', key: 'fund_type' },
  { title: 'Адрес', key: 'address.line' },
  { title: 'Описание', key: 'description' },
  { title: 'Действия', key: 'actions', sortable: false, align: 'end' },
]

const resetForm = () => {
  form.id = null
  form.name = ''
  form.fund_type = 'other'
  form.description = ''
  form.address_id = null
  form.address_line = ''
}

const loadFunds = async () => {
  loading.value = true
  try {
    const { data } = await apiClient.get('/funds/', { params: { page_size: 200 } })
    funds.value = data.results ?? data
  } finally {
    loading.value = false
  }
}

const loadAddresses = async () => {
  const { data } = await apiClient.get('/addresses/', { params: { page_size: 200 } })
  addresses.value = data.results ?? data
}

const ensureAddress = async () => {
  if (form.address_id) return form.address_id
  if (!form.address_line) return null
  const { data } = await apiClient.post('/addresses/', { line: form.address_line })
  await loadAddresses()
  form.address_id = data.id
  return data.id
}

const openCreate = () => {
  resetForm()
  isEdit.value = false
  dialog.value = true
}

const openEdit = (fund) => {
  resetForm()
  isEdit.value = true
  form.id = fund.id
  form.name = fund.name
  form.fund_type = fund.fund_type
  form.description = fund.description
  form.address_id = fund.address?.id || null
  form.address_line = fund.address?.line || ''
  dialog.value = true
}

const saveFund = async () => {
  loading.value = true
  try {
    const addressId = await ensureAddress()
    const payload = {
      name: form.name,
      fund_type: form.fund_type,
      description: form.description,
      address_id: addressId,
    }
    if (isEdit.value && form.id) {
      await apiClient.patch(`/funds/${form.id}/`, payload)
    } else {
      await apiClient.post('/funds/', payload)
    }
    dialog.value = false
    await loadFunds()
  } finally {
    loading.value = false
  }
}

const deleteFund = async (fund) => {
  if (!confirm(`Удалить фонд "${fund.name}"?`)) return
  await apiClient.delete(`/funds/${fund.id}/`)
  await loadFunds()
}

onMounted(async () => {
  await Promise.all([loadFunds(), loadAddresses()])
})
</script>

<template>
  <v-container fluid class="py-6">
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <div>
          <div class="text-h5">Фонды хранения</div>
          <div class="text-body-2 text-medium-emphasis">Администрирование фондов и адресов</div>
        </div>
        <v-btn color="primary" @click="openCreate">
          <v-icon class="mr-2">mdi-plus</v-icon>
          Добавить фонд
        </v-btn>
      </v-card-title>
      <v-data-table
        :headers="headers"
        :items="funds"
        :loading="loading"
        class="border-t"
      >
        <template #item.fund_type="{ item }">
          {{ FUND_TYPES.find((type) => type.value === item.fund_type)?.title || item.fund_type }}
        </template>
        <template #item['address.line']="{ item }">
          {{ item.address?.line || '—' }}
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
            @click="deleteFund(item)"
          />
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="dialog" max-width="600">
      <v-card>
        <v-card-title>
          {{ isEdit ? 'Редактирование фонда' : 'Создание фонда' }}
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="saveFund">
            <v-text-field
              v-model="form.name"
              label="Название"
              required
            />
            <v-select
              v-model="form.fund_type"
              :items="FUND_TYPES"
              item-title="title"
              item-value="value"
              label="Тип фонда"
            />
            <v-autocomplete
              v-model="form.address_id"
              :items="addresses"
              item-title="line"
              item-value="id"
              label="Адрес (выберите существующий)"
              clearable
            />
            <v-text-field
              v-model="form.address_line"
              label="Новый адрес"
              hint="Если указан, будет создан новый адрес"
            />
            <v-textarea
              v-model="form.description"
              label="Описание"
              rows="3"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="dialog = false">Отмена</v-btn>
          <v-btn color="primary" :loading="loading" @click="saveFund">
            Сохранить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>


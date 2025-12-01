<script setup>
import { reactive, ref, onMounted } from 'vue'
import { apiClient } from '@/services/http'

const loading = ref(false)
const items = ref([])
const report = reactive({
  exhibitionsCount: [],
  collectionItems: [],
  relatedItems: [],
  writtenOff: [],
  fundVolume: [],
})
const filters = reactive({
  writtenOffFrom: '',
  writtenOffTo: '',
  relatedItemId: '',
})

const fetchReports = async () => {
  loading.value = true
  try {
    const [
      exhibitionsRes,
      collectionsRes,
      volumeRes,
      itemsRes,
    ] = await Promise.all([
      apiClient.get('/funds/exhibitions_count/'),
      apiClient.get('/collections/', { params: { page_size: 200 } }),
      apiClient.get('/items/fund_volume_percentage/'),
      apiClient.get('/items/', { params: { page_size: 200 } }),
    ])
    report.exhibitionsCount = exhibitionsRes.data
    report.collectionItems = (collectionsRes.data.results ?? collectionsRes.data).map((col) => ({
      id: col.id,
      name: col.name,
      items_count: col.items_count,
    }))
    report.fundVolume = volumeRes.data
    items.value = itemsRes.data.results ?? itemsRes.data

    await loadWrittenOff()
    if (report.collectionItems.length > 0) {
      filters.relatedItemId = null
      report.relatedItems = []
    }
  } finally {
    loading.value = false
  }
}

const loadRelatedItems = async () => {
  if (!filters.relatedItemId) {
    report.relatedItems = []
    return
  }
  const { data } = await apiClient.get(`/items/${filters.relatedItemId}/related_by_exhibitions/`)
  report.relatedItems = data
}

const loadWrittenOff = async () => {
  const { data } = await apiClient.get('/items/written_off_count_by_fund/', {
    params: {
      from: filters.writtenOffFrom || undefined,
      to: filters.writtenOffTo || undefined,
    },
  })
  report.writtenOff = data
}

onMounted(fetchReports)
</script>

<template>
  <v-container fluid class="py-6">
    <v-row>
      <v-col cols="12" md="6">
        <v-card :loading="loading">
          <v-card-title>1. Выставки по фондам</v-card-title>
          <v-data-table
            :headers="[
              { title: 'Фонд', key: 'name' },
              { title: 'Выставок', key: 'exhibitions_count', align: 'end' },
            ]"
            :items="report.exhibitionsCount"
            density="comfortable"
            hide-default-footer
          />
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card :loading="loading">
          <v-card-title>2. Размеры комплектов</v-card-title>
          <v-data-table
            :headers="[
              { title: 'Комплект', key: 'name' },
              { title: 'Единиц', key: 'items_count', align: 'end' },
            ]"
            :items="report.collectionItems"
            density="comfortable"
            hide-default-footer
          />
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-2">
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span>3. Связанные предметы</span>
            <v-autocomplete
              v-model="filters.relatedItemId"
              :items="items"
              item-title="name"
              item-value="id"
              label="Выберите предмет"
              hide-details
              density="compact"
              style="max-width: 280px"
              @update:model-value="loadRelatedItems"
            />
          </v-card-title>
          <v-data-table
            :headers="[
              { title: 'Инв. номер', key: 'inventory_number' },
              { title: 'Название', key: 'name' },
              { title: 'Фонд', key: 'fund.name' },
            ]"
            :items="report.relatedItems"
            density="compact"
            hide-default-footer
          />
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center flex-wrap ga-4">
            <span>4. Списанные предметы по фондам</span>
            <div class="d-flex ga-2 align-center">
              <v-text-field
                v-model="filters.writtenOffFrom"
                type="date"
                label="С"
                hide-details
                density="compact"
                style="max-width: 150px"
              />
              <v-text-field
                v-model="filters.writtenOffTo"
                type="date"
                label="По"
                hide-details
                density="compact"
                style="max-width: 150px"
              />
              <v-btn
                size="small"
                color="primary"
                @click="loadWrittenOff"
              >
                Обновить
              </v-btn>
            </div>
          </v-card-title>
          <v-data-table
            :headers="[
              { title: 'Фонд', key: 'item__fund__name' },
              { title: 'Количество', key: 'written_off_count', align: 'end' },
            ]"
            :items="report.writtenOff"
            density="compact"
            hide-default-footer
          />
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-2">
      <v-col cols="12">
        <v-card>
          <v-card-title>5. Процентное соотношение фондов</v-card-title>
          <v-data-table
            :headers="[
              { title: 'Фонд', key: 'name' },
              { title: 'Единиц', key: 'count', align: 'end' },
              { title: 'Доля, %', key: 'percentage', align: 'end' },
            ]"
            :items="report.fundVolume"
            density="compact"
          />
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>


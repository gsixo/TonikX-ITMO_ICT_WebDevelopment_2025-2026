<script setup>
import { reactive, onMounted } from 'vue'
import { apiClient } from '@/services/http'

const state = reactive({
  loading: false,
  fundReport: null,
  fundVolumes: [],
  exhibitionsCount: [],
  error: '',
})

const loadDashboard = async () => {
  state.loading = true
  state.error = ''
  try {
    const [reportRes, volumeRes, exhibitionsRes] = await Promise.all([
      apiClient.get('/funds/full_report/'),
      apiClient.get('/items/fund_volume_percentage/'),
      apiClient.get('/funds/exhibitions_count/'),
    ])
    state.fundReport = reportRes.data
    state.fundVolumes = volumeRes.data
    state.exhibitionsCount = exhibitionsRes.data
  } catch (error) {
    state.error = error.response?.data?.detail || 'Не удалось загрузить данные'
  } finally {
    state.loading = false
  }
}

onMounted(loadDashboard)
</script>

<template>
  <v-container fluid class="py-6">
    <v-alert
      v-if="state.error"
      type="error"
      class="mb-4"
      border="start"
    >
      {{ state.error }}
    </v-alert>
    <v-row>
      <v-col cols="12" md="4">
        <v-card :loading="state.loading">
          <v-card-title>
            <v-icon class="mr-2">mdi-warehouse</v-icon>
            Всего фондов
          </v-card-title>
          <v-card-text class="text-h4">
            {{ state.fundReport?.funds.length || 0 }}
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card :loading="state.loading">
          <v-card-title>
            <v-icon class="mr-2">mdi-package-variant</v-icon>
            Музейных предметов
          </v-card-title>
          <v-card-text class="text-h4">
            {{ state.fundReport?.total_items || 0 }}
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card :loading="state.loading">
          <v-card-title>
            <v-icon class="mr-2">mdi-chart-pie</v-icon>
            Отчётов доступно
          </v-card-title>
          <v-card-text class="text-h4">
            5
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-2">
      <v-col cols="12" md="6">
        <v-card :loading="state.loading">
          <v-card-title>Процент фонда в коллекции</v-card-title>
          <v-data-table
            :headers="[
              { title: 'Фонд', key: 'name' },
              { title: 'Единиц', key: 'count', align: 'end' },
              { title: 'Доля, %', key: 'percentage', align: 'end' },
            ]"
            :items="state.fundVolumes"
            density="compact"
            hide-default-footer
          />
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card :loading="state.loading">
          <v-card-title>Количество выставок по фондам</v-card-title>
          <v-data-table
            :headers="[
              { title: 'Фонд', key: 'name' },
              { title: 'Выставок', key: 'exhibitions_count', align: 'end' },
            ]"
            :items="state.exhibitionsCount"
            density="compact"
            hide-default-footer
          />
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-2">
      <v-col cols="12">
        <v-card :loading="state.loading">
          <v-card-title>Карточки фондов</v-card-title>
          <v-expansion-panels>
            <v-expansion-panel
              v-for="fund in state.fundReport?.funds || []"
              :key="fund.fund_id"
            >
              <v-expansion-panel-title>
                <div class="d-flex justify-space-between align-center w-100">
                  <div>{{ fund.fund_name }}</div>
                  <v-chip color="primary" variant="flat" size="small">
                    {{ fund.items_count }} предметов
                  </v-chip>
                </div>
              </v-expansion-panel-title>
              <v-expansion-panel-content>
                <v-data-table
                  :headers="[
                    { title: 'Инвентарный номер', key: 'inventory_number' },
                    { title: 'Название', key: 'name' },
                    { title: 'Первая приёмка', key: 'first_receive_date' },
                    { title: 'Выставок', key: 'exhibitions_count', align: 'end' },
                    { title: 'Списан', key: 'is_written_off', align: 'center' },
                  ]"
                  :items="fund.items"
                  density="compact"
                  :items-per-page="10"
                >
                  <template #item.is_written_off="{ item }">
                    <v-chip
                      :color="item.is_written_off ? 'error' : 'success'"
                      variant="elevated"
                      size="small"
                    >
                      {{ item.is_written_off ? 'Да' : 'Нет' }}
                    </v-chip>
                  </template>
                </v-data-table>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>


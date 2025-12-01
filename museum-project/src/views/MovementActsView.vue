<script setup>
import { ref, reactive, onMounted } from 'vue'
import { apiClient } from '@/services/http'

const movementActs = ref([])
const funds = ref([])
const items = ref([])
const collections = ref([])
const organizations = ref([])
const exhibitions = ref([])
const loading = ref(false)
const actDialog = ref(false)
const movementDialog = ref(false)
const selectedAct = ref(null)

const actForm = reactive({
  act_number: '',
  movement_type: 'receive',
  museum_director_name: '',
  fund_keeper_name: '',
  notes: '',
})

const movementForm = reactive({
  act: null,
  movement_type: 'receive',
  item_id: null,
  collection_id: null,
  external_organization_id: null,
  exhibition_id: null,
  from_fund_id: null,
  to_fund_id: null,
  date: '',
  note: '',
})

const MOVEMENT_TYPES = [
  { value: 'receive', title: 'Приём на хранение' },
  { value: 'transfer_exhibition', title: 'Передача на выставку' },
  { value: 'return', title: 'Возвращение с выставки' },
  { value: 'write_off', title: 'Списание' },
  { value: 'internal_transfer', title: 'Внутренний перевод' },
]

const loadActs = async () => {
  loading.value = true
  try {
    const { data } = await apiClient.get('/movement-acts/', { params: { page_size: 100 } })
    movementActs.value = data.results ?? data
  } finally {
    loading.value = false
  }
}

const loadLookups = async () => {
  const [fundsRes, itemsRes, collectionsRes, orgRes, exhibitionsRes] = await Promise.all([
    apiClient.get('/funds/', { params: { page_size: 200 } }),
    apiClient.get('/items/', { params: { page_size: 200 } }),
    apiClient.get('/collections/', { params: { page_size: 200 } }),
    apiClient.get('/organizations/', { params: { page_size: 200 } }),
    apiClient.get('/exhibitions/', { params: { page_size: 200 } }),
  ])
  funds.value = fundsRes.data.results ?? fundsRes.data
  items.value = itemsRes.data.results ?? itemsRes.data
  collections.value = collectionsRes.data.results ?? collectionsRes.data
  organizations.value = orgRes.data.results ?? orgRes.data
  exhibitions.value = exhibitionsRes.data.results ?? exhibitionsRes.data
}

const openActDialog = () => {
  actForm.act_number = ''
  actForm.movement_type = 'receive'
  actForm.museum_director_name = ''
  actForm.fund_keeper_name = ''
  actForm.notes = ''
  actDialog.value = true
}

const saveAct = async () => {
  await apiClient.post('/movement-acts/', {
    act_number: actForm.act_number,
    movement_type: actForm.movement_type,
    museum_director_name: actForm.museum_director_name,
    fund_keeper_name: actForm.fund_keeper_name,
    notes: actForm.notes,
  })
  actDialog.value = false
  await loadActs()
}

const openMovementDialog = (act) => {
  selectedAct.value = act
  movementForm.act = act.id
  movementForm.movement_type = act.movement_type
  movementForm.item_id = null
  movementForm.collection_id = null
  movementForm.external_organization_id = null
  movementForm.exhibition_id = null
  movementForm.from_fund_id = null
  movementForm.to_fund_id = null
  movementForm.date = new Date().toISOString().slice(0, 10)
  movementForm.note = ''
  movementDialog.value = true
}

const saveMovement = async () => {
  await apiClient.post('/movements/', {
    act: movementForm.act,
    movement_type: movementForm.movement_type,
    item_id: movementForm.item_id,
    collection_id: movementForm.collection_id,
    external_organization_id: movementForm.external_organization_id,
    exhibition_id: movementForm.exhibition_id,
    from_fund_id: movementForm.from_fund_id,
    to_fund_id: movementForm.to_fund_id,
    date: movementForm.date,
    note: movementForm.note,
  })
  movementDialog.value = false
  await loadActs()
}

onMounted(async () => {
  await Promise.all([loadActs(), loadLookups()])
})
</script>

<template>
  <v-container fluid class="py-6">
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <div>
          <div class="text-h5">Движения и акты</div>
          <div class="text-body-2 text-medium-emphasis">
            Учёт приёмов, передач и внутренних перемещений
          </div>
        </div>
        <v-btn color="primary" @click="openActDialog">
          <v-icon class="mr-2">mdi-file-plus</v-icon>
          Новый акт
        </v-btn>
      </v-card-title>
      <v-expansion-panels>
        <v-expansion-panel
          v-for="act in movementActs"
          :key="act.id"
        >
          <v-expansion-panel-title>
            <div class="d-flex flex-column flex-sm-row justify-space-between w-100">
              <div>
                <strong>Акт №{{ act.act_number }}</strong>
                <div class="text-caption text-medium-emphasis">
                  {{ MOVEMENT_TYPES.find((type) => type.value === act.movement_type)?.title }}
                </div>
              </div>
              <div class="text-caption text-medium-emphasis">
                Создан: {{ new Date(act.created_at).toLocaleString() }}
              </div>
            </div>
          </v-expansion-panel-title>
          <v-expansion-panel-content>
            <v-card-text>
              <div class="mb-4">
                <div><strong>Директор:</strong> {{ act.museum_director_name || '—' }}</div>
                <div><strong>Хранитель:</strong> {{ act.fund_keeper_name || '—' }}</div>
                <div><strong>Примечания:</strong> {{ act.notes || '—' }}</div>
              </div>
              <v-data-table
                :headers="[
                  { title: 'Тип', key: 'movement_type' },
                  { title: 'Предмет/комплект', key: 'target' },
                  { title: 'Организация', key: 'external_organization.name' },
                  { title: 'Выставка', key: 'exhibition.name' },
                  { title: 'Дата', key: 'date' },
                ]"
                :items="act.movements || []"
                density="compact"
                hide-default-footer
              >
                <template #item.movement_type="{ item }">
                  {{ MOVEMENT_TYPES.find((type) => type.value === item.movement_type)?.title }}
                </template>
                <template #item.target="{ item }">
                  <div v-if="item.item">
                    {{ item.item.inventory_number }} — {{ item.item.name }}
                  </div>
                  <div v-else-if="item.collection">
                    Комплект: {{ item.collection.name }}
                  </div>
                  <div v-else>—</div>
                </template>
              </v-data-table>
              <v-btn
                color="secondary"
                class="mt-4"
                variant="tonal"
                @click="openMovementDialog(act)"
              >
                Добавить движение
              </v-btn>
            </v-card-text>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-card>

    <v-dialog v-model="actDialog" max-width="600">
      <v-card>
        <v-card-title>Новый акт движения</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="saveAct">
            <v-text-field
              v-model="actForm.act_number"
              label="Номер акта"
              required
            />
            <v-select
              v-model="actForm.movement_type"
              :items="MOVEMENT_TYPES"
              item-title="title"
              item-value="value"
              label="Тип движения"
              required
            />
            <v-text-field
              v-model="actForm.museum_director_name"
              label="Руководитель музея"
            />
            <v-text-field
              v-model="actForm.fund_keeper_name"
              label="Хранитель фонда"
            />
            <v-textarea
              v-model="actForm.notes"
              label="Примечания"
              rows="3"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="actDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="saveAct">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="movementDialog" max-width="700">
      <v-card>
        <v-card-title>Новое перемещение</v-card-title>
        <v-card-text>
          <div class="text-body-2 mb-4">
            Акт №{{ selectedAct?.act_number }}
          </div>
          <v-form @submit.prevent="saveMovement">
            <v-select
              v-model="movementForm.movement_type"
              :items="MOVEMENT_TYPES"
              item-title="title"
              item-value="value"
              label="Тип движения"
            />
            <v-select
              v-model="movementForm.item_id"
              :items="items"
              item-title="name"
              item-value="id"
              label="Предмет"
              clearable
            />
            <v-select
              v-model="movementForm.collection_id"
              :items="collections"
              item-title="name"
              item-value="id"
              label="Комплект"
              clearable
            />
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="movementForm.from_fund_id"
                  :items="funds"
                  item-title="name"
                  item-value="id"
                  label="Из фонда"
                  clearable
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="movementForm.to_fund_id"
                  :items="funds"
                  item-title="name"
                  item-value="id"
                  label="В фонд"
                  clearable
                />
              </v-col>
            </v-row>
            <v-select
              v-model="movementForm.external_organization_id"
              :items="organizations"
              item-title="name"
              item-value="id"
              label="Организация"
              clearable
            />
            <v-select
              v-model="movementForm.exhibition_id"
              :items="exhibitions"
              item-title="name"
              item-value="id"
              label="Выставка"
              clearable
            />
            <v-text-field
              v-model="movementForm.date"
              label="Дата"
              type="date"
              required
            />
            <v-textarea
              v-model="movementForm.note"
              label="Примечание"
              rows="2"
            />
          </v-form>
        </v-card-text>
        <v-card-actions class="justify-end">
          <v-btn variant="text" @click="movementDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="saveMovement">Добавить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>


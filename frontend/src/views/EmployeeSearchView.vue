<script setup lang="ts">
import { downloadObjektivka, exportEmployeesToExcel, searchEmployees } from '@/api/employees'
import { EMPLOYMENT_STATUS_LABELS } from '@/constants/labels'
import type { EmployeeSearchFilter, EmployeeSearchResult } from '@/types/employee'
import { reactive, ref } from 'vue'

const filters = reactive<EmployeeSearchFilter>({
  page: 1,
  page_size: 25,
})

const result = ref<EmployeeSearchResult | null>(null)
const loading = ref(false)

async function runSearch() {
  loading.value = true
  try {
    result.value = await searchEmployees(filters)
  } finally {
    loading.value = false
  }
}

runSearch()
</script>

<template>
  <div class="mx-auto max-w-6xl p-6">
    <div class="mb-4 flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-slate-800">Xodimlarni qidirish</h1>
      <RouterLink :to="{ name: 'employee-create' }" class="rounded bg-slate-800 px-4 py-2 text-sm text-white hover:bg-slate-700">
        + Yangi xodim
      </RouterLink>
    </div>

    <!-- Bu — Advanced Search'ning ilyustrativ namunasi: 3 ta filtr ko'rsatilgan, backend
    EmployeeSearchFilter esa 14 tagacha parametrni qo'llab-quvvatlaydi (app/schemas/search.py).
    Qolgan filtrlar (bo'lim, jins, yosh oralig'i va h.k.) xuddi shu naqsh bo'yicha qo'shiladi. -->
    <form
      class="mb-6 grid grid-cols-1 gap-4 rounded-lg bg-white p-4 shadow sm:grid-cols-3"
      @submit.prevent="runSearch"
    >
      <div>
        <label class="mb-1 block text-sm text-slate-600">F.I.Sh.</label>
        <input v-model="filters.full_name" type="text" class="w-full rounded border px-3 py-2" />
      </div>

      <div>
        <label class="mb-1 block text-sm text-slate-600">Mutaxassislik sohasi</label>
        <input
          v-model="filters.specialization_area"
          type="text"
          placeholder="masalan: IT"
          class="w-full rounded border px-3 py-2"
        />
      </div>

      <div>
        <label class="mb-1 block text-sm text-slate-600">Joriy lavozimda (kamida, yil)</label>
        <input
          v-model.number="filters.min_years_in_position"
          type="number"
          min="0"
          class="w-full rounded border px-3 py-2"
        />
      </div>

      <div class="flex items-end gap-3 sm:col-span-3">
        <button type="submit" class="rounded bg-slate-800 px-4 py-2 text-white hover:bg-slate-700">
          Qidirish
        </button>
        <button
          type="button"
          class="rounded border border-slate-300 px-4 py-2 text-slate-700 hover:bg-slate-50"
          @click="exportEmployeesToExcel(filters)"
        >
          Excel'ga eksport
        </button>
      </div>
    </form>

    <p v-if="loading">Yuklanmoqda...</p>

    <table v-else-if="result" class="w-full rounded-lg bg-white shadow">
      <thead>
        <tr class="border-b text-left text-sm text-slate-500">
          <th class="p-3">F.I.Sh.</th>
          <th class="p-3">Lavozimi</th>
          <th class="p-3">Holati</th>
          <th class="p-3">Soha</th>
          <th class="p-3">Obyektivka</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in result.items" :key="item.id" class="border-b text-sm">
          <td class="p-3">
            <RouterLink :to="{ name: 'employee-detail', params: { id: item.id } }" class="text-blue-600 hover:underline">
              {{ item.full_name }}
            </RouterLink>
          </td>
          <td class="p-3">{{ item.position?.title ?? '—' }}</td>
          <td class="p-3">{{ EMPLOYMENT_STATUS_LABELS[item.employment_status] }}</td>
          <td class="p-3">{{ item.specialization_area ?? '—' }}</td>
          <td class="p-3">
            <button class="text-blue-600 hover:underline" @click="downloadObjektivka(item.id, item.full_name)">
              Yuklab olish
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-if="result" class="mt-3 text-sm text-slate-500">Jami: {{ result.total }} ta natija</p>
  </div>
</template>

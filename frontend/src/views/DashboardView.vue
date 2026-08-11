<script setup lang="ts">
import { getDashboardStats } from '@/api/dashboard'
import BarChart from '@/components/BarChart.vue'
import type { DashboardStats } from '@/types/employee'
import { onMounted, ref } from 'vue'

const stats = ref<DashboardStats | null>(null)
const loading = ref(true)

onMounted(async () => {
  loading.value = true
  try {
    stats.value = await getDashboardStats()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="mx-auto max-w-4xl p-6">
    <h1 class="mb-4 text-2xl font-semibold text-slate-800">Statistika</h1>

    <p v-if="loading">Yuklanmoqda...</p>

    <template v-else-if="stats">
      <div class="mb-6 rounded-lg bg-white p-5 shadow">
        <span class="text-xs text-slate-400">Jami xodimlar (arxivlanmagan)</span>
        <p class="text-4xl font-semibold text-slate-800">{{ stats.total_employees }}</p>
      </div>

      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <section class="rounded-lg bg-white p-5 shadow">
          <h2 class="mb-3 text-lg font-semibold text-slate-800">Jinsi bo'yicha</h2>
          <BarChart :data="stats.by_gender" />
        </section>

        <section class="rounded-lg bg-white p-5 shadow">
          <h2 class="mb-3 text-lg font-semibold text-slate-800">Ish holati bo'yicha</h2>
          <BarChart :data="stats.by_employment_status" />
        </section>

        <section class="rounded-lg bg-white p-5 shadow">
          <h2 class="mb-3 text-lg font-semibold text-slate-800">Yosh oralig'i bo'yicha</h2>
          <BarChart :data="stats.by_age_bucket" />
        </section>

        <section class="rounded-lg bg-white p-5 shadow">
          <h2 class="mb-3 text-lg font-semibold text-slate-800">Ta'lim darajasi bo'yicha</h2>
          <BarChart :data="stats.by_education_level" />
        </section>

        <section class="rounded-lg bg-white p-5 shadow sm:col-span-2">
          <h2 class="mb-3 text-lg font-semibold text-slate-800">Bo'limlar bo'yicha</h2>
          <BarChart :data="stats.by_department" />
        </section>
      </div>
    </template>
  </div>
</template>

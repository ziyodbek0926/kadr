<script setup lang="ts">
import { foreignTripsApi } from '@/api/employees'
import type { ForeignTripInput, ForeignTripRead } from '@/types/employee'
import { ref } from 'vue'

const props = defineProps<{ employeeId: number; items: ForeignTripRead[] }>()
const emit = defineEmits<{ changed: [] }>()

function emptyForm(): ForeignTripInput {
  return { country: '', purpose: null, start_date: '', end_date: null, order_basis: null }
}

const showForm = ref(false)
const form = ref<ForeignTripInput>(emptyForm())
const saving = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  saving.value = true
  try {
    await foreignTripsApi.add(props.employeeId, form.value)
    form.value = emptyForm()
    showForm.value = false
    emit('changed')
  } catch {
    error.value = "Saqlashda xatolik yuz berdi"
  } finally {
    saving.value = false
  }
}

async function remove(id: number) {
  if (!confirm("Bu yozuvni o'chirishni tasdiqlaysizmi?")) return
  await foreignTripsApi.remove(props.employeeId, id)
  emit('changed')
}
</script>

<template>
  <section class="rounded-lg bg-white p-5 shadow">
    <div class="mb-3 flex items-center justify-between">
      <h2 class="text-lg font-semibold text-slate-800">Xorijga chiqishlari</h2>
      <button class="text-sm text-blue-600 hover:underline" @click="showForm = !showForm">
        {{ showForm ? 'Bekor qilish' : '+ Qo\'shish' }}
      </button>
    </div>

    <table v-if="items.length" class="mb-3 w-full text-sm">
      <thead>
        <tr class="border-b text-left text-slate-500">
          <th class="p-2">Davlat</th>
          <th class="p-2">Maqsadi</th>
          <th class="p-2">Davri</th>
          <th class="p-2">Asos hujjat</th>
          <th class="p-2"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id" class="border-b">
          <td class="p-2">{{ item.country }}</td>
          <td class="p-2">{{ item.purpose ?? '—' }}</td>
          <td class="p-2">{{ item.start_date }} — {{ item.end_date ?? '—' }}</td>
          <td class="p-2">{{ item.order_basis ?? '—' }}</td>
          <td class="p-2 text-right">
            <button class="text-red-600 hover:underline" @click="remove(item.id)">O'chirish</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="mb-3 text-sm text-slate-400">Ma'lumot kiritilmagan.</p>

    <form v-if="showForm" class="grid grid-cols-1 gap-3 rounded border bg-slate-50 p-4 sm:grid-cols-3" @submit.prevent="submit">
      <div>
        <label class="mb-1 block text-xs text-slate-600">Davlat</label>
        <input v-model="form.country" required class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Boshlanish sanasi</label>
        <input v-model="form.start_date" type="date" required class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Tugash sanasi</label>
        <input v-model="form.end_date" type="date" class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Maqsadi</label>
        <input v-model="form.purpose" class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Asos hujjat</label>
        <input v-model="form.order_basis" class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <p v-if="error" class="text-sm text-red-600 sm:col-span-3">{{ error }}</p>
      <div class="sm:col-span-3">
        <button type="submit" :disabled="saving" class="rounded bg-slate-800 px-4 py-1.5 text-sm text-white disabled:opacity-50">
          {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
        </button>
      </div>
    </form>
  </section>
</template>

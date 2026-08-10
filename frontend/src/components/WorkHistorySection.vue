<script setup lang="ts">
import { workHistoryApi } from '@/api/employees'
import type { WorkHistoryInput, WorkHistoryRead } from '@/types/employee'
import { ref } from 'vue'

const props = defineProps<{ employeeId: number; items: WorkHistoryRead[] }>()
const emit = defineEmits<{ changed: [] }>()

function emptyForm(): WorkHistoryInput {
  return { organization_name: '', position_title: '', start_date: '', end_date: null, order_reference: null, notes: null }
}

const showForm = ref(false)
const form = ref<WorkHistoryInput>(emptyForm())
const saving = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  saving.value = true
  try {
    await workHistoryApi.add(props.employeeId, form.value)
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
  await workHistoryApi.remove(props.employeeId, id)
  emit('changed')
}
</script>

<template>
  <section class="rounded-lg bg-white p-5 shadow">
    <div class="mb-3 flex items-center justify-between">
      <h2 class="text-lg font-semibold text-slate-800">Mehnat faoliyati tarixi</h2>
      <button class="text-sm text-blue-600 hover:underline" @click="showForm = !showForm">
        {{ showForm ? 'Bekor qilish' : '+ Qo\'shish' }}
      </button>
    </div>

    <table v-if="items.length" class="mb-3 w-full text-sm">
      <thead>
        <tr class="border-b text-left text-slate-500">
          <th class="p-2">Tashkilot</th>
          <th class="p-2">Lavozim</th>
          <th class="p-2">Davri</th>
          <th class="p-2">Buyruq asosida</th>
          <th class="p-2"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id" class="border-b">
          <td class="p-2">{{ item.organization_name }}</td>
          <td class="p-2">{{ item.position_title }}</td>
          <td class="p-2">{{ item.start_date }} — {{ item.end_date ?? 'hozirgacha' }}</td>
          <td class="p-2">{{ item.order_reference ?? '—' }}</td>
          <td class="p-2 text-right">
            <button class="text-red-600 hover:underline" @click="remove(item.id)">O'chirish</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="mb-3 text-sm text-slate-400">Ma'lumot kiritilmagan.</p>

    <form v-if="showForm" class="grid grid-cols-1 gap-3 rounded border bg-slate-50 p-4 sm:grid-cols-3" @submit.prevent="submit">
      <div>
        <label class="mb-1 block text-xs text-slate-600">Tashkilot</label>
        <input v-model="form.organization_name" required class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Lavozim</label>
        <input v-model="form.position_title" required class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Buyruq asosi</label>
        <input v-model="form.order_reference" class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Boshlanish sanasi</label>
        <input v-model="form.start_date" type="date" required class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Tugash sanasi (bo'sh = hozirgacha)</label>
        <input v-model="form.end_date" type="date" class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Izoh</label>
        <input v-model="form.notes" class="w-full rounded border px-2 py-1.5 text-sm" />
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

<script setup lang="ts">
import { educationApi } from '@/api/employees'
import { EDUCATION_LEVEL_LABELS } from '@/constants/labels'
import type { EducationHistoryInput, EducationHistoryRead, EducationLevel } from '@/types/employee'
import { ref } from 'vue'

const props = defineProps<{ employeeId: number; items: EducationHistoryRead[] }>()
const emit = defineEmits<{ changed: [] }>()

function emptyForm(): EducationHistoryInput {
  return { institution_name: '', specialty: null, level: 'bachelor', start_date: null, end_date: null, document_number: null }
}

const showForm = ref(false)
const form = ref<EducationHistoryInput>(emptyForm())
const saving = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  saving.value = true
  try {
    await educationApi.add(props.employeeId, form.value)
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
  await educationApi.remove(props.employeeId, id)
  emit('changed')
}
</script>

<template>
  <section class="rounded-lg bg-white p-5 shadow">
    <div class="mb-3 flex items-center justify-between">
      <h2 class="text-lg font-semibold text-slate-800">Ta'lim tarixi</h2>
      <button class="text-sm text-blue-600 hover:underline" @click="showForm = !showForm">
        {{ showForm ? 'Bekor qilish' : '+ Qo\'shish' }}
      </button>
    </div>

    <table v-if="items.length" class="mb-3 w-full text-sm">
      <thead>
        <tr class="border-b text-left text-slate-500">
          <th class="p-2">O'quv muassasasi</th>
          <th class="p-2">Mutaxassisligi</th>
          <th class="p-2">Daraja</th>
          <th class="p-2">Davri</th>
          <th class="p-2"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id" class="border-b">
          <td class="p-2">{{ item.institution_name }}</td>
          <td class="p-2">{{ item.specialty ?? '—' }}</td>
          <td class="p-2">{{ EDUCATION_LEVEL_LABELS[item.level] }}</td>
          <td class="p-2">{{ item.start_date ?? '—' }} — {{ item.end_date ?? '—' }}</td>
          <td class="p-2 text-right">
            <button class="text-red-600 hover:underline" @click="remove(item.id)">O'chirish</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="mb-3 text-sm text-slate-400">Ma'lumot kiritilmagan.</p>

    <form v-if="showForm" class="grid grid-cols-1 gap-3 rounded border bg-slate-50 p-4 sm:grid-cols-3" @submit.prevent="submit">
      <div class="sm:col-span-2">
        <label class="mb-1 block text-xs text-slate-600">O'quv muassasasi</label>
        <input v-model="form.institution_name" required class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Daraja</label>
        <select v-model="(form.level as EducationLevel)" class="w-full rounded border px-2 py-1.5 text-sm">
          <option v-for="(label, value) in EDUCATION_LEVEL_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Mutaxassisligi</label>
        <input v-model="form.specialty" class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Boshlanish sanasi</label>
        <input v-model="form.start_date" type="date" class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Tugash sanasi</label>
        <input v-model="form.end_date" type="date" class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Hujjat raqami</label>
        <input v-model="form.document_number" class="w-full rounded border px-2 py-1.5 text-sm" />
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

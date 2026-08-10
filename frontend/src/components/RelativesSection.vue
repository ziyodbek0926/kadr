<script setup lang="ts">
import { relativesApi } from '@/api/employees'
import { RELATIVE_TYPE_LABELS } from '@/constants/labels'
import type { RelativeInput, RelativeRead, RelativeType } from '@/types/employee'
import { ref } from 'vue'

const props = defineProps<{ employeeId: number; items: RelativeRead[] }>()
const emit = defineEmits<{ changed: [] }>()

function emptyForm(): RelativeInput {
  return {
    relation_type: 'father',
    full_name: '',
    birth_year: null,
    birth_place: null,
    workplace: null,
    position_title: null,
    address: null,
  }
}

const showForm = ref(false)
const form = ref<RelativeInput>(emptyForm())
const saving = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  saving.value = true
  try {
    await relativesApi.add(props.employeeId, form.value)
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
  await relativesApi.remove(props.employeeId, id)
  emit('changed')
}
</script>

<template>
  <section class="rounded-lg bg-white p-5 shadow">
    <div class="mb-3 flex items-center justify-between">
      <h2 class="text-lg font-semibold text-slate-800">Yaqin qarindoshlari</h2>
      <button class="text-sm text-blue-600 hover:underline" @click="showForm = !showForm">
        {{ showForm ? 'Bekor qilish' : '+ Qo\'shish' }}
      </button>
    </div>

    <table v-if="items.length" class="mb-3 w-full text-sm">
      <thead>
        <tr class="border-b text-left text-slate-500">
          <th class="p-2">Qarindoshlik</th>
          <th class="p-2">F.I.Sh.</th>
          <th class="p-2">Tug'ilgan yili</th>
          <th class="p-2">Ish joyi / lavozimi</th>
          <th class="p-2">Manzili</th>
          <th class="p-2"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id" class="border-b">
          <td class="p-2">{{ RELATIVE_TYPE_LABELS[item.relation_type] }}</td>
          <td class="p-2">{{ item.full_name }}</td>
          <td class="p-2">{{ item.birth_year ?? '—' }}</td>
          <td class="p-2">{{ [item.workplace, item.position_title].filter(Boolean).join(', ') || '—' }}</td>
          <td class="p-2">{{ item.address ?? '—' }}</td>
          <td class="p-2 text-right">
            <button class="text-red-600 hover:underline" @click="remove(item.id)">O'chirish</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="mb-3 text-sm text-slate-400">Ma'lumot kiritilmagan.</p>

    <form v-if="showForm" class="grid grid-cols-1 gap-3 rounded border bg-slate-50 p-4 sm:grid-cols-3" @submit.prevent="submit">
      <div>
        <label class="mb-1 block text-xs text-slate-600">Qarindoshlik turi</label>
        <select v-model="(form.relation_type as RelativeType)" class="w-full rounded border px-2 py-1.5 text-sm">
          <option v-for="(label, value) in RELATIVE_TYPE_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">F.I.Sh.</label>
        <input v-model="form.full_name" required class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Tug'ilgan yili</label>
        <input v-model.number="form.birth_year" type="number" class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Ish joyi</label>
        <input v-model="form.workplace" class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Lavozimi</label>
        <input v-model="form.position_title" class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Yashash manzili</label>
        <input v-model="form.address" class="w-full rounded border px-2 py-1.5 text-sm" />
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

<script setup lang="ts">
import { awardsApi } from '@/api/employees'
import type { AwardInput, AwardRead } from '@/types/employee'
import { ref } from 'vue'

const props = defineProps<{ employeeId: number; items: AwardRead[] }>()
const emit = defineEmits<{ changed: [] }>()

function emptyForm(): AwardInput {
  return { name: '', awarded_date: '', recommending_organization: null }
}

const showForm = ref(false)
const form = ref<AwardInput>(emptyForm())
const saving = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  saving.value = true
  try {
    await awardsApi.add(props.employeeId, form.value)
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
  await awardsApi.remove(props.employeeId, id)
  emit('changed')
}
</script>

<template>
  <section class="rounded-lg bg-white p-5 shadow">
    <div class="mb-3 flex items-center justify-between">
      <h2 class="text-lg font-semibold text-slate-800">Mukofotlar</h2>
      <button class="text-sm text-blue-600 hover:underline" @click="showForm = !showForm">
        {{ showForm ? 'Bekor qilish' : '+ Qo\'shish' }}
      </button>
    </div>

    <table v-if="items.length" class="mb-3 w-full text-sm">
      <thead>
        <tr class="border-b text-left text-slate-500">
          <th class="p-2">Mukofot nomi</th>
          <th class="p-2">Sanasi</th>
          <th class="p-2">Tavsiya etgan tashkilot</th>
          <th class="p-2"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id" class="border-b">
          <td class="p-2">{{ item.name }}</td>
          <td class="p-2">{{ item.awarded_date }}</td>
          <td class="p-2">{{ item.recommending_organization ?? '—' }}</td>
          <td class="p-2 text-right">
            <button class="text-red-600 hover:underline" @click="remove(item.id)">O'chirish</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="mb-3 text-sm text-slate-400">Mukofotlari yo'q.</p>

    <form v-if="showForm" class="grid grid-cols-1 gap-3 rounded border bg-slate-50 p-4 sm:grid-cols-3" @submit.prevent="submit">
      <div>
        <label class="mb-1 block text-xs text-slate-600">Mukofot nomi</label>
        <input v-model="form.name" required class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Sanasi</label>
        <input v-model="form.awarded_date" type="date" required class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Tavsiya etgan tashkilot</label>
        <input v-model="form.recommending_organization" class="w-full rounded border px-2 py-1.5 text-sm" />
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

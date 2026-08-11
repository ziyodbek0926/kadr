<script setup lang="ts">
import { createEmployee } from '@/api/employees'
import PositionSelect from '@/components/PositionSelect.vue'
import { GENDER_LABELS } from '@/constants/labels'
import type { EmployeeInput } from '@/types/employee'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const saving = ref(false)
const error = ref('')

const form = ref<EmployeeInput>({
  last_name: '',
  first_name: '',
  middle_name: null,
  birth_date: '',
  birth_place: null,
  gender: 'male',
  nationality: null,
  citizenship: "O'zbekiston Respublikasi",
  position_id: null,
  employment_status: 'active',
})

async function submit() {
  error.value = ''
  saving.value = true
  try {
    const created = await createEmployee(form.value)
    router.push({ name: 'employee-detail', params: { id: created.id } })
  } catch {
    error.value = "Saqlashda xatolik yuz berdi — majburiy maydonlarni (F.I.Sh., tug'ilgan sana, jinsi) tekshiring"
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl p-6">
    <h1 class="mb-4 text-2xl font-semibold text-slate-800">Yangi xodim qo'shish</h1>
    <p class="mb-4 text-sm text-slate-500">
      Asosiy ma'lumotlarni kiriting — saqlangandan so'ng qarindoshlari, ta'limi, mehnat
      faoliyati va boshqa ma'lumotlarni xodim kartasida to'ldirasiz.
    </p>

    <form class="grid grid-cols-1 gap-3 rounded-lg bg-white p-5 shadow sm:grid-cols-3" @submit.prevent="submit">
      <div><label class="mb-1 block text-xs text-slate-600">Familiya *</label><input v-model="form.last_name" required class="w-full rounded border px-2 py-1.5 text-sm" /></div>
      <div><label class="mb-1 block text-xs text-slate-600">Ism *</label><input v-model="form.first_name" required class="w-full rounded border px-2 py-1.5 text-sm" /></div>
      <div><label class="mb-1 block text-xs text-slate-600">Sharifi</label><input v-model="form.middle_name" class="w-full rounded border px-2 py-1.5 text-sm" /></div>

      <div><label class="mb-1 block text-xs text-slate-600">Tug'ilgan sana *</label><input v-model="form.birth_date" type="date" required class="w-full rounded border px-2 py-1.5 text-sm" /></div>
      <div><label class="mb-1 block text-xs text-slate-600">Tug'ilgan joyi</label><input v-model="form.birth_place" class="w-full rounded border px-2 py-1.5 text-sm" /></div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Jinsi *</label>
        <select v-model="form.gender" class="w-full rounded border px-2 py-1.5 text-sm">
          <option v-for="(label, value) in GENDER_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>

      <div><label class="mb-1 block text-xs text-slate-600">Millati</label><input v-model="form.nationality" class="w-full rounded border px-2 py-1.5 text-sm" /></div>
      <div><label class="mb-1 block text-xs text-slate-600">Fuqaroligi</label><input v-model="form.citizenship" class="w-full rounded border px-2 py-1.5 text-sm" /></div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Lavozimi</label>
        <PositionSelect v-model="form.position_id" />
      </div>

      <div class="sm:col-span-3"><label class="mb-1 block text-xs text-slate-600">PINFL (14 xonali, ixtiyoriy)</label><input v-model="form.pinfl" maxlength="14" class="w-full rounded border px-2 py-1.5 text-sm" /></div>

      <p v-if="error" class="text-sm text-red-600 sm:col-span-3">{{ error }}</p>
      <div class="sm:col-span-3">
        <button type="submit" :disabled="saving" class="rounded bg-slate-800 px-4 py-2 text-sm text-white disabled:opacity-50">
          {{ saving ? 'Saqlanmoqda...' : "Saqlash va davom etish" }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { listEmployees } from '@/api/employees'
import { createUser, deactivateUser, listUsers } from '@/api/users'
import { USER_ROLE_LABELS } from '@/constants/labels'
import { useAuthStore } from '@/stores/auth'
import type { EmployeeListItem, UserCreateInput, UserRead, UserRoleCode } from '@/types/employee'
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'

const auth = useAuthStore()

const users = ref<UserRead[]>([])
const employees = ref<EmployeeListItem[]>([])
const loading = ref(true)
const error = ref('')

function extractError(e: unknown): string {
  if (axios.isAxiosError(e) && typeof e.response?.data?.detail === 'string') {
    return e.response.data.detail
  }
  return 'Amalni bajarishda xatolik yuz berdi'
}

async function loadAll() {
  const [userList, employeeList] = await Promise.all([listUsers(), listEmployees({ limit: 500 })])
  users.value = userList
  employees.value = employeeList
}

onMounted(async () => {
  if (!auth.isSuperAdmin) return
  loading.value = true
  try {
    await loadAll()
  } finally {
    loading.value = false
  }
})

const showAddForm = ref(false)
const roleOptions = Object.entries(USER_ROLE_LABELS) as [UserRoleCode, string][]

function emptyForm(): UserCreateInput {
  return { username: '', password: '', full_name: '', role_code: 'hr_operator', employee_id: null }
}

const form = ref<UserCreateInput>(emptyForm())
const saving = ref(false)

async function submitNewUser() {
  error.value = ''
  saving.value = true
  try {
    await createUser(form.value)
    form.value = emptyForm()
    showAddForm.value = false
    await loadAll()
  } catch (e) {
    error.value = extractError(e)
  } finally {
    saving.value = false
  }
}

async function deactivate(user: UserRead) {
  if (!confirm(`"${user.username}" hisobini faolsizlantirishni tasdiqlaysizmi?`)) return
  error.value = ''
  try {
    await deactivateUser(user.id)
    await loadAll()
  } catch (e) {
    error.value = extractError(e)
  }
}

function formatDate(iso: string | null): string {
  return iso ? iso.slice(0, 10) : '—'
}
</script>

<template>
  <div class="mx-auto max-w-4xl p-6">
    <h1 class="mb-4 text-2xl font-semibold text-slate-800">Foydalanuvchilar</h1>

    <p v-if="!auth.isSuperAdmin" class="rounded-lg bg-white p-5 text-sm text-slate-500 shadow">
      Bu sahifa faqat SuperAdmin uchun.
    </p>

    <template v-else>
      <p v-if="error" class="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-600">{{ error }}</p>

      <div class="mb-4 flex justify-end">
        <button class="rounded bg-slate-800 px-4 py-2 text-sm text-white hover:bg-slate-700" @click="showAddForm = !showAddForm">
          {{ showAddForm ? 'Bekor qilish' : "+ Yangi foydalanuvchi" }}
        </button>
      </div>

      <form
        v-if="showAddForm"
        class="mb-6 grid grid-cols-1 gap-3 rounded-lg border bg-slate-50 p-4 sm:grid-cols-2"
        @submit.prevent="submitNewUser"
      >
        <div>
          <label class="mb-1 block text-xs text-slate-600">Login</label>
          <input v-model="form.username" required minlength="3" class="w-full rounded border px-2 py-1.5 text-sm" />
          <p class="mt-1 text-xs text-slate-400">Faqat lotin harflari, raqam, "_" va "."</p>
        </div>
        <div>
          <label class="mb-1 block text-xs text-slate-600">F.I.Sh.</label>
          <input v-model="form.full_name" required minlength="2" class="w-full rounded border px-2 py-1.5 text-sm" />
        </div>
        <div>
          <label class="mb-1 block text-xs text-slate-600">Parol</label>
          <input
            v-model="form.password"
            type="password"
            required
            minlength="10"
            class="w-full rounded border px-2 py-1.5 text-sm"
          />
          <p class="mt-1 text-xs text-slate-400">Kamida 10 belgi, katta va kichik harf, raqam bo'lishi shart</p>
        </div>
        <div>
          <label class="mb-1 block text-xs text-slate-600">Roli</label>
          <select v-model="form.role_code" class="w-full rounded border px-2 py-1.5 text-sm">
            <option v-for="[code, label] in roleOptions" :key="code" :value="code">{{ label }}</option>
          </select>
        </div>
        <div class="sm:col-span-2">
          <label class="mb-1 block text-xs text-slate-600">Bog'liq xodim (ixtiyoriy)</label>
          <select v-model="form.employee_id" class="w-full rounded border px-2 py-1.5 text-sm">
            <option :value="null">— Bog'lamaslik —</option>
            <option v-for="e in employees" :key="e.id" :value="e.id">{{ e.full_name }}</option>
          </select>
        </div>
        <div class="sm:col-span-2">
          <button type="submit" :disabled="saving" class="rounded bg-slate-800 px-4 py-1.5 text-sm text-white disabled:opacity-50">
            {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>

      <p v-if="loading">Yuklanmoqda...</p>

      <table v-else class="w-full rounded-lg bg-white text-sm shadow">
        <thead>
          <tr class="border-b text-left text-slate-500">
            <th class="p-3">Login</th>
            <th class="p-3">F.I.Sh.</th>
            <th class="p-3">Roli</th>
            <th class="p-3">Holati</th>
            <th class="p-3">Oxirgi kirish</th>
            <th class="p-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id" class="border-b">
            <td class="p-3">{{ u.username }}</td>
            <td class="p-3">{{ u.full_name }}</td>
            <td class="p-3">{{ u.role.display_name }}</td>
            <td class="p-3">
              <span
                class="rounded px-2 py-0.5 text-xs"
                :class="u.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-500'"
              >
                {{ u.is_active ? 'Faol' : 'Nofaol' }}
              </span>
            </td>
            <td class="p-3">{{ formatDate(u.last_login_at) }}</td>
            <td class="p-3 text-right">
              <button
                v-if="u.is_active"
                class="text-red-600 hover:underline"
                @click="deactivate(u)"
              >
                Faolsizlantirish
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </template>
  </div>
</template>

<script setup lang="ts">
import {
  createDepartment,
  createPosition,
  deleteDepartment,
  deletePosition,
  listDepartments,
  listPositions,
  updateDepartment,
  updatePosition,
} from '@/api/departments'
import { useAuthStore } from '@/stores/auth'
import type { DepartmentRead, PositionReadWithDepartment } from '@/types/employee'
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'

const auth = useAuthStore()
const canEdit = computed(() => auth.canEdit)

const departments = ref<DepartmentRead[]>([])
const positions = ref<PositionReadWithDepartment[]>([])
const loading = ref(true)
const error = ref('')

function extractError(e: unknown): string {
  if (axios.isAxiosError(e) && typeof e.response?.data?.detail === 'string') {
    return e.response.data.detail
  }
  return 'Amalni bajarishda xatolik yuz berdi'
}

async function loadAll() {
  const [depList, posList] = await Promise.all([listDepartments(), listPositions()])
  departments.value = depList
  positions.value = posList
}

onMounted(async () => {
  loading.value = true
  try {
    await loadAll()
  } finally {
    loading.value = false
  }
})

interface DeptRow {
  dept: DepartmentRead
  depth: number
}

const departmentRows = computed<DeptRow[]>(() => {
  const byParent = new Map<number | null, DepartmentRead[]>()
  for (const d of departments.value) {
    const key = d.parent_id
    if (!byParent.has(key)) byParent.set(key, [])
    byParent.get(key)!.push(d)
  }

  const rows: DeptRow[] = []
  function walk(parentId: number | null, depth: number) {
    for (const child of byParent.get(parentId) ?? []) {
      rows.push({ dept: child, depth })
      walk(child.id, depth + 1)
    }
  }
  walk(null, 0)

  // Ehtiyot chorasi: agar parent_id ro'yxatda yo'q bo'lsa (odatiy holatda bo'lmasligi kerak), baribir ko'rsatiladi
  const visited = new Set(rows.map((r) => r.dept.id))
  for (const d of departments.value) {
    if (!visited.has(d.id)) rows.push({ dept: d, depth: 0 })
  }
  return rows
})

const positionsByDept = computed<Map<number, PositionReadWithDepartment[]>>(() => {
  const map = new Map<number, PositionReadWithDepartment[]>()
  for (const p of positions.value) {
    if (!map.has(p.department_id)) map.set(p.department_id, [])
    map.get(p.department_id)!.push(p)
  }
  return map
})

// ---- Bo'lim qo'shish ----

const showAddDept = ref(false)
const newDeptName = ref('')
const newDeptParentId = ref<number | null>(null)

async function submitNewDept() {
  error.value = ''
  if (!newDeptName.value.trim()) {
    error.value = "Bo'lim nomini kiriting"
    return
  }
  try {
    await createDepartment({ name: newDeptName.value.trim(), parent_id: newDeptParentId.value })
    newDeptName.value = ''
    newDeptParentId.value = null
    showAddDept.value = false
    await loadAll()
  } catch (e) {
    error.value = extractError(e)
  }
}

// ---- Bo'limni tahrirlash/o'chirish ----

const editingDeptId = ref<number | null>(null)
const editDeptForm = ref<{ name: string; parent_id: number | null }>({ name: '', parent_id: null })

function startEditDept(dept: DepartmentRead) {
  editingDeptId.value = dept.id
  editDeptForm.value = { name: dept.name, parent_id: dept.parent_id }
  error.value = ''
}

async function saveEditDept(deptId: number) {
  error.value = ''
  if (!editDeptForm.value.name.trim()) {
    error.value = "Bo'lim nomini kiriting"
    return
  }
  try {
    await updateDepartment(deptId, editDeptForm.value)
    editingDeptId.value = null
    await loadAll()
  } catch (e) {
    error.value = extractError(e)
  }
}

async function removeDept(dept: DepartmentRead) {
  if (!confirm(`"${dept.name}" bo'limini o'chirishni tasdiqlaysizmi?`)) return
  error.value = ''
  try {
    await deleteDepartment(dept.id)
    await loadAll()
  } catch (e) {
    error.value = extractError(e)
  }
}

// ---- Lavozim qo'shish ----

const addPositionForDept = ref<number | null>(null)
const newPositionTitle = ref('')
const newPositionCategory = ref('')

function toggleAddPosition(departmentId: number) {
  addPositionForDept.value = addPositionForDept.value === departmentId ? null : departmentId
  newPositionTitle.value = ''
  newPositionCategory.value = ''
  error.value = ''
}

async function submitNewPosition(departmentId: number) {
  error.value = ''
  if (!newPositionTitle.value.trim()) {
    error.value = "Lavozim nomini kiriting"
    return
  }
  try {
    await createPosition({
      title: newPositionTitle.value.trim(),
      department_id: departmentId,
      category: newPositionCategory.value.trim() || null,
      is_vacant: true,
    })
    addPositionForDept.value = null
    await loadAll()
  } catch (e) {
    error.value = extractError(e)
  }
}

// ---- Lavozimni tahrirlash/o'chirish ----

const editingPositionId = ref<number | null>(null)
const editPositionForm = ref<{ title: string; department_id: number; category: string | null; is_vacant: boolean }>({
  title: '',
  department_id: 0,
  category: null,
  is_vacant: true,
})

function startEditPosition(p: PositionReadWithDepartment) {
  editingPositionId.value = p.id
  editPositionForm.value = {
    title: p.title,
    department_id: p.department_id,
    category: p.category,
    is_vacant: p.is_vacant,
  }
  error.value = ''
}

async function saveEditPosition(id: number) {
  error.value = ''
  if (!editPositionForm.value.title.trim()) {
    error.value = "Lavozim nomini kiriting"
    return
  }
  try {
    await updatePosition(id, editPositionForm.value)
    editingPositionId.value = null
    await loadAll()
  } catch (e) {
    error.value = extractError(e)
  }
}

async function removePosition(p: PositionReadWithDepartment) {
  if (!confirm(`"${p.title}" lavozimini o'chirishni tasdiqlaysizmi?`)) return
  error.value = ''
  try {
    await deletePosition(p.id)
    await loadAll()
  } catch (e) {
    error.value = extractError(e)
  }
}
</script>

<template>
  <div class="mx-auto max-w-4xl p-6">
    <div class="mb-4 flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-slate-800">Bo'limlar va lavozimlar</h1>
      <button
        v-if="canEdit"
        class="rounded bg-slate-800 px-4 py-2 text-sm text-white hover:bg-slate-700"
        @click="showAddDept = !showAddDept"
      >
        {{ showAddDept ? 'Bekor qilish' : "+ Yangi bo'lim" }}
      </button>
    </div>

    <p v-if="error" class="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-600">{{ error }}</p>

    <form
      v-if="showAddDept"
      class="mb-6 grid grid-cols-1 gap-3 rounded-lg border bg-slate-50 p-4 sm:grid-cols-3"
      @submit.prevent="submitNewDept"
    >
      <div class="sm:col-span-2">
        <label class="mb-1 block text-xs text-slate-600">Bo'lim nomi</label>
        <input v-model="newDeptName" required class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Yuqori bo'lim (ixtiyoriy)</label>
        <select v-model="newDeptParentId" class="w-full rounded border px-2 py-1.5 text-sm">
          <option :value="null">— Yo'q (tepa daraja) —</option>
          <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </div>
      <div class="sm:col-span-3">
        <button type="submit" class="rounded bg-slate-800 px-4 py-1.5 text-sm text-white">Saqlash</button>
      </div>
    </form>

    <p v-if="loading">Yuklanmoqda...</p>

    <div v-else class="space-y-4">
      <div
        v-for="row in departmentRows"
        :key="row.dept.id"
        class="rounded-lg bg-white p-4 shadow"
        :style="{ marginLeft: `${row.depth * 20}px` }"
      >
        <div v-if="editingDeptId === row.dept.id" class="grid grid-cols-1 gap-2 sm:grid-cols-3">
          <input v-model="editDeptForm.name" class="rounded border px-2 py-1.5 text-sm sm:col-span-2" />
          <select v-model="editDeptForm.parent_id" class="rounded border px-2 py-1.5 text-sm">
            <option :value="null">— Yo'q (tepa daraja) —</option>
            <option v-for="d in departments" :key="d.id" :value="d.id" :disabled="d.id === row.dept.id">{{ d.name }}</option>
          </select>
          <div class="flex gap-2 sm:col-span-3">
            <button class="rounded bg-slate-800 px-3 py-1 text-xs text-white" @click="saveEditDept(row.dept.id)">Saqlash</button>
            <button class="rounded border px-3 py-1 text-xs" @click="editingDeptId = null">Bekor qilish</button>
          </div>
        </div>
        <div v-else class="flex items-center justify-between">
          <h2 class="font-semibold text-slate-800">{{ row.dept.name }}</h2>
          <div v-if="canEdit" class="flex gap-3 text-sm">
            <button class="text-blue-600 hover:underline" @click="startEditDept(row.dept)">Tahrirlash</button>
            <button class="text-red-600 hover:underline" @click="removeDept(row.dept)">O'chirish</button>
          </div>
        </div>

        <table v-if="positionsByDept.get(row.dept.id)?.length" class="mt-3 w-full text-sm">
          <thead>
            <tr class="border-b text-left text-slate-500">
              <th class="p-2">Lavozim</th>
              <th class="p-2">Toifa</th>
              <th class="p-2">Holati</th>
              <th class="p-2"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in positionsByDept.get(row.dept.id)" :key="p.id" class="border-b">
              <template v-if="editingPositionId === p.id">
                <td class="p-2" colspan="4">
                  <div class="grid grid-cols-1 gap-2 sm:grid-cols-4">
                    <input v-model="editPositionForm.title" class="rounded border px-2 py-1 text-sm sm:col-span-2" />
                    <input v-model="editPositionForm.category" placeholder="Toifa" class="rounded border px-2 py-1 text-sm" />
                    <label class="flex items-center gap-1 text-xs text-slate-600">
                      <input v-model="editPositionForm.is_vacant" type="checkbox" /> Bo'sh
                    </label>
                    <div class="flex gap-2 sm:col-span-4">
                      <button class="rounded bg-slate-800 px-3 py-1 text-xs text-white" @click="saveEditPosition(p.id)">
                        Saqlash
                      </button>
                      <button class="rounded border px-3 py-1 text-xs" @click="editingPositionId = null">Bekor qilish</button>
                    </div>
                  </div>
                </td>
              </template>
              <template v-else>
                <td class="p-2">{{ p.title }}</td>
                <td class="p-2">{{ p.category ?? '—' }}</td>
                <td class="p-2">
                  <span
                    class="rounded px-2 py-0.5 text-xs"
                    :class="p.is_vacant ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'"
                  >
                    {{ p.is_vacant ? "Bo'sh" : 'Band' }}
                  </span>
                </td>
                <td class="p-2 text-right">
                  <span v-if="canEdit" class="flex justify-end gap-3">
                    <button class="text-blue-600 hover:underline" @click="startEditPosition(p)">Tahrirlash</button>
                    <button class="text-red-600 hover:underline" @click="removePosition(p)">O'chirish</button>
                  </span>
                </td>
              </template>
            </tr>
          </tbody>
        </table>
        <p v-else class="mt-3 text-sm text-slate-400">Lavozimlar kiritilmagan.</p>

        <div v-if="canEdit" class="mt-3">
          <button class="text-sm text-blue-600 hover:underline" @click="toggleAddPosition(row.dept.id)">
            {{ addPositionForDept === row.dept.id ? 'Bekor qilish' : '+ Yangi lavozim' }}
          </button>
          <form
            v-if="addPositionForDept === row.dept.id"
            class="mt-2 grid grid-cols-1 gap-2 rounded border bg-slate-50 p-3 sm:grid-cols-3"
            @submit.prevent="submitNewPosition(row.dept.id)"
          >
            <input v-model="newPositionTitle" placeholder="Lavozim nomi" required class="rounded border px-2 py-1.5 text-sm" />
            <input v-model="newPositionCategory" placeholder="Toifa (ixtiyoriy)" class="rounded border px-2 py-1.5 text-sm" />
            <button type="submit" class="rounded bg-slate-800 px-3 py-1.5 text-sm text-white">Saqlash</button>
          </form>
        </div>
      </div>

      <p v-if="!departmentRows.length" class="text-sm text-slate-400">Hali bo'limlar kiritilmagan.</p>
    </div>
  </div>
</template>

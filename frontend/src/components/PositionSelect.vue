<script setup lang="ts">
import { createDepartment, createPosition, listDepartments, listPositions } from '@/api/departments'
import type { DepartmentRead, PositionReadWithDepartment } from '@/types/employee'
import { onMounted, ref } from 'vue'

const modelValue = defineModel<number | null>({ default: null })

const positions = ref<PositionReadWithDepartment[]>([])
const departments = ref<DepartmentRead[]>([])

const showAdd = ref(false)
const creatingDepartment = ref(false)
const newTitle = ref('')
const newDepartmentId = ref<number | null>(null)
const newDepartmentName = ref('')
const saving = ref(false)
const error = ref('')

async function loadAll() {
  const [posList, depList] = await Promise.all([listPositions(), listDepartments()])
  positions.value = posList
  departments.value = depList
}

onMounted(loadAll)

function resetAddForm() {
  showAdd.value = false
  creatingDepartment.value = false
  newTitle.value = ''
  newDepartmentId.value = null
  newDepartmentName.value = ''
  error.value = ''
}

async function submitNewPosition() {
  error.value = ''
  if (!newTitle.value.trim()) {
    error.value = 'Lavozim nomini kiriting'
    return
  }
  if (!creatingDepartment.value && !newDepartmentId.value) {
    error.value = "Bo'limni tanlang yoki yangi bo'lim qo'shing"
    return
  }
  if (creatingDepartment.value && !newDepartmentName.value.trim()) {
    error.value = "Bo'lim nomini kiriting"
    return
  }

  saving.value = true
  try {
    let departmentId = newDepartmentId.value
    if (creatingDepartment.value) {
      const dep = await createDepartment({ name: newDepartmentName.value.trim(), parent_id: null })
      departmentId = dep.id
    }
    const position = await createPosition({
      title: newTitle.value.trim(),
      department_id: departmentId as number,
      category: null,
      is_vacant: true,
    })
    await loadAll()
    modelValue.value = position.id
    resetAddForm()
  } catch {
    error.value = "Saqlashda xatolik yuz berdi"
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <select v-model="modelValue" class="w-full rounded border px-2 py-1.5 text-sm">
      <option :value="null">—</option>
      <option v-for="p in positions" :key="p.id" :value="p.id">{{ p.department.name }} — {{ p.title }}</option>
    </select>
    <button type="button" class="mt-1 text-xs text-blue-600 hover:underline" @click="showAdd = !showAdd">
      {{ showAdd ? 'Bekor qilish' : "+ Ro'yxatda yo'q lavozimni qo'shish" }}
    </button>

    <div v-if="showAdd" class="mt-2 space-y-2 rounded border bg-slate-50 p-3">
      <div>
        <label class="mb-1 block text-xs text-slate-600">Bo'lim</label>
        <select v-if="!creatingDepartment" v-model="newDepartmentId" class="w-full rounded border px-2 py-1.5 text-sm">
          <option :value="null">— Bo'limni tanlang —</option>
          <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
        <input
          v-else
          v-model="newDepartmentName"
          placeholder="Yangi bo'lim nomi"
          class="w-full rounded border px-2 py-1.5 text-sm"
        />
        <button type="button" class="mt-1 text-xs text-blue-600 hover:underline" @click="creatingDepartment = !creatingDepartment">
          {{ creatingDepartment ? "Mavjud bo'limdan tanlash" : "+ Yangi bo'lim" }}
        </button>
      </div>
      <div>
        <label class="mb-1 block text-xs text-slate-600">Yangi lavozim nomi</label>
        <input v-model="newTitle" placeholder="masalan: Bosh mutaxassis" class="w-full rounded border px-2 py-1.5 text-sm" />
      </div>
      <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
      <button
        type="button"
        :disabled="saving"
        class="rounded bg-slate-800 px-3 py-1 text-xs text-white disabled:opacity-50"
        @click="submitNewPosition"
      >
        {{ saving ? 'Saqlanmoqda...' : "Qo'shish va tanlash" }}
      </button>
    </div>
  </div>
</template>

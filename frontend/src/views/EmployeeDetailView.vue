<script setup lang="ts">
import { deleteEmployee, downloadObjektivka, getEmployee, getEmployeeSensitive, updateEmployee } from '@/api/employees'
import AwardsSection from '@/components/AwardsSection.vue'
import DocumentAttachmentsSection from '@/components/DocumentAttachmentsSection.vue'
import EducationSection from '@/components/EducationSection.vue'
import ForeignTripsSection from '@/components/ForeignTripsSection.vue'
import PositionSelect from '@/components/PositionSelect.vue'
import RelativesSection from '@/components/RelativesSection.vue'
import WorkHistorySection from '@/components/WorkHistorySection.vue'
import { EDUCATION_LEVEL_LABELS, EMPLOYMENT_STATUS_LABELS, GENDER_LABELS, MARITAL_STATUS_LABELS } from '@/constants/labels'
import { useAuthStore } from '@/stores/auth'
import type { EmployeeDetailRead, EmployeeInput, EmployeeSensitiveRead } from '@/types/employee'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const employeeId = Number(route.params.id)
const employee = ref<EmployeeDetailRead | null>(null)
const loading = ref(true)
const editing = ref(false)
const saving = ref(false)
const error = ref('')

const sensitive = ref<EmployeeSensitiveRead | null>(null)
const sensitiveLoading = ref(false)

const canEdit = computed(() => auth.canEdit)
const canDelete = computed(() => auth.role === 'super_admin')

const form = ref<EmployeeInput>(blankForm())

function blankForm(): EmployeeInput {
  return {
    last_name: '',
    first_name: '',
    middle_name: null,
    birth_date: '',
    birth_place: null,
    gender: 'male',
    nationality: null,
    citizenship: "O'zbekiston Respublikasi",
    marital_status: null,
    academic_degree: null,
    academic_title: null,
    foreign_languages: null,
    military_rank: null,
    party_affiliation: null,
    public_office_note: null,
    current_address: null,
    permanent_address: null,
    phone_number: null,
    position_id: null,
    position_since: null,
    hire_date: null,
    employment_status: 'active',
    specialization_area: null,
    positive_traits: null,
    negative_traits: null,
  }
}

function syncFormFromEmployee(emp: EmployeeDetailRead) {
  form.value = {
    last_name: emp.last_name,
    first_name: emp.first_name,
    middle_name: emp.middle_name,
    birth_date: emp.birth_date,
    birth_place: emp.birth_place,
    gender: emp.gender,
    nationality: emp.nationality,
    citizenship: emp.citizenship,
    marital_status: emp.marital_status,
    academic_degree: emp.academic_degree,
    academic_title: emp.academic_title,
    foreign_languages: emp.foreign_languages,
    military_rank: emp.military_rank,
    party_affiliation: emp.party_affiliation,
    public_office_note: emp.public_office_note,
    current_address: emp.current_address,
    permanent_address: emp.permanent_address,
    phone_number: emp.phone_number,
    position_id: emp.position?.id ?? null,
    position_since: emp.position_since,
    hire_date: emp.hire_date,
    employment_status: emp.employment_status,
    specialization_area: emp.specialization_area,
    positive_traits: emp.positive_traits,
    negative_traits: emp.negative_traits,
  }
}

async function reload() {
  employee.value = await getEmployee(employeeId)
  syncFormFromEmployee(employee.value)
}

onMounted(async () => {
  loading.value = true
  try {
    await reload()
  } finally {
    loading.value = false
  }
})

async function saveForm() {
  error.value = ''
  saving.value = true
  try {
    employee.value = await updateEmployee(employeeId, form.value)
    editing.value = false
  } catch {
    error.value = "Saqlashda xatolik yuz berdi — maydonlarni tekshiring"
  } finally {
    saving.value = false
  }
}

async function revealSensitive() {
  sensitiveLoading.value = true
  try {
    sensitive.value = await getEmployeeSensitive(employeeId)
  } finally {
    sensitiveLoading.value = false
  }
}

async function download() {
  if (!employee.value) return
  await downloadObjektivka(employeeId, employee.value.full_name)
}

async function archiveEmployee() {
  if (!confirm("Xodimni arxivlashni tasdiqlaysizmi? Bu amalni faqat SuperAdmin bekor qila oladi.")) return
  await deleteEmployee(employeeId)
  router.push({ name: 'search' })
}

function goBack() {
  router.push({ name: 'search' })
}
</script>

<template>
  <div class="mx-auto max-w-5xl p-6">
    <button class="mb-4 text-sm text-slate-500 hover:underline" @click="goBack">&larr; Qidiruvga qaytish</button>

    <p v-if="loading">Yuklanmoqda...</p>

    <template v-else-if="employee">
      <div class="mb-6 flex flex-wrap items-start justify-between gap-4 rounded-lg bg-white p-5 shadow">
        <div>
          <h1 class="text-2xl font-semibold text-slate-800">{{ employee.full_name }}</h1>
          <p class="mt-1 text-slate-500">
            {{ employee.position?.title ?? "Lavozim belgilanmagan" }}
            <span v-if="employee.position"> — {{ EMPLOYMENT_STATUS_LABELS[employee.employment_status] }}</span>
          </p>
        </div>
        <div class="flex gap-2">
          <button class="rounded bg-slate-800 px-4 py-2 text-sm text-white hover:bg-slate-700" @click="download">
            Obyektivka yuklab olish
          </button>
          <button
            v-if="canEdit"
            class="rounded border border-slate-300 px-4 py-2 text-sm hover:bg-slate-50"
            @click="editing = !editing"
          >
            {{ editing ? 'Bekor qilish' : 'Tahrirlash' }}
          </button>
          <button
            v-if="canDelete"
            class="rounded border border-red-300 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
            @click="archiveEmployee"
          >
            Arxivlash
          </button>
        </div>
      </div>

      <!-- Faqat o'qish ko'rinishi -->
      <div v-if="!editing" class="mb-6 grid grid-cols-1 gap-4 rounded-lg bg-white p-5 shadow sm:grid-cols-3">
        <div><span class="text-xs text-slate-400">Tug'ilgan sana</span><p>{{ employee.birth_date }}</p></div>
        <div><span class="text-xs text-slate-400">Tug'ilgan joyi</span><p>{{ employee.birth_place ?? '—' }}</p></div>
        <div><span class="text-xs text-slate-400">Jinsi</span><p>{{ GENDER_LABELS[employee.gender] }}</p></div>
        <div><span class="text-xs text-slate-400">Millati</span><p>{{ employee.nationality ?? '—' }}</p></div>
        <div><span class="text-xs text-slate-400">Fuqaroligi</span><p>{{ employee.citizenship ?? '—' }}</p></div>
        <div>
          <span class="text-xs text-slate-400">Oilaviy holati</span>
          <p>{{ employee.marital_status ? MARITAL_STATUS_LABELS[employee.marital_status] : '—' }}</p>
        </div>
        <div><span class="text-xs text-slate-400">Ilmiy darajasi</span><p>{{ employee.academic_degree ?? '—' }}</p></div>
        <div><span class="text-xs text-slate-400">Ilmiy unvoni</span><p>{{ employee.academic_title ?? '—' }}</p></div>
        <div><span class="text-xs text-slate-400">Chet tillari</span><p>{{ employee.foreign_languages ?? '—' }}</p></div>
        <div><span class="text-xs text-slate-400">Joriy manzil</span><p>{{ employee.current_address ?? '—' }}</p></div>
        <div><span class="text-xs text-slate-400">Doimiy manzil</span><p>{{ employee.permanent_address ?? '—' }}</p></div>
        <div><span class="text-xs text-slate-400">Telefon</span><p>{{ employee.phone_number ?? '—' }}</p></div>
        <div><span class="text-xs text-slate-400">Joriy lavozimda</span><p>{{ employee.position_since ?? '—' }}</p></div>
        <div><span class="text-xs text-slate-400">Ishga kirgan sana</span><p>{{ employee.hire_date ?? '—' }}</p></div>
        <div><span class="text-xs text-slate-400">Mutaxassislik sohasi</span><p>{{ employee.specialization_area ?? '—' }}</p></div>

        <div class="sm:col-span-3 border-t pt-3">
          <button v-if="canEdit && !sensitive" class="text-sm text-blue-600 hover:underline" :disabled="sensitiveLoading" @click="revealSensitive">
            {{ sensitiveLoading ? 'Yuklanmoqda...' : "PINFL / pasport ma'lumotlarini ko'rsatish" }}
          </button>
          <div v-else-if="sensitive" class="text-sm text-slate-600">
            <span class="font-medium">PINFL:</span> {{ sensitive.pinfl ?? "kiritilmagan" }}
            &nbsp;&nbsp;
            <span class="font-medium">Pasport raqami:</span> {{ sensitive.passport_number ?? "kiritilmagan" }}
            <span class="ml-2 text-xs text-slate-400">(bu ko'rish audit-logga yozildi)</span>
          </div>
        </div>
      </div>

      <!-- Tahrirlash formasi -->
      <form v-else class="mb-6 rounded-lg bg-white p-5 shadow" @submit.prevent="saveForm">
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div><label class="mb-1 block text-xs text-slate-600">Familiya</label><input v-model="form.last_name" required class="w-full rounded border px-2 py-1.5 text-sm" /></div>
          <div><label class="mb-1 block text-xs text-slate-600">Ism</label><input v-model="form.first_name" required class="w-full rounded border px-2 py-1.5 text-sm" /></div>
          <div><label class="mb-1 block text-xs text-slate-600">Sharifi</label><input v-model="form.middle_name" class="w-full rounded border px-2 py-1.5 text-sm" /></div>

          <div><label class="mb-1 block text-xs text-slate-600">Tug'ilgan sana</label><input v-model="form.birth_date" type="date" required class="w-full rounded border px-2 py-1.5 text-sm" /></div>
          <div><label class="mb-1 block text-xs text-slate-600">Tug'ilgan joyi</label><input v-model="form.birth_place" class="w-full rounded border px-2 py-1.5 text-sm" /></div>
          <div>
            <label class="mb-1 block text-xs text-slate-600">Jinsi</label>
            <select v-model="form.gender" class="w-full rounded border px-2 py-1.5 text-sm">
              <option v-for="(label, value) in GENDER_LABELS" :key="value" :value="value">{{ label }}</option>
            </select>
          </div>

          <div><label class="mb-1 block text-xs text-slate-600">Millati</label><input v-model="form.nationality" class="w-full rounded border px-2 py-1.5 text-sm" /></div>
          <div><label class="mb-1 block text-xs text-slate-600">Fuqaroligi</label><input v-model="form.citizenship" class="w-full rounded border px-2 py-1.5 text-sm" /></div>
          <div>
            <label class="mb-1 block text-xs text-slate-600">Oilaviy holati</label>
            <select v-model="form.marital_status" class="w-full rounded border px-2 py-1.5 text-sm">
              <option :value="null">—</option>
              <option v-for="(label, value) in MARITAL_STATUS_LABELS" :key="value" :value="value">{{ label }}</option>
            </select>
          </div>

          <div><label class="mb-1 block text-xs text-slate-600">Ilmiy darajasi</label><input v-model="form.academic_degree" class="w-full rounded border px-2 py-1.5 text-sm" /></div>
          <div><label class="mb-1 block text-xs text-slate-600">Ilmiy unvoni</label><input v-model="form.academic_title" class="w-full rounded border px-2 py-1.5 text-sm" /></div>
          <div><label class="mb-1 block text-xs text-slate-600">Chet tillari</label><input v-model="form.foreign_languages" class="w-full rounded border px-2 py-1.5 text-sm" /></div>

          <div><label class="mb-1 block text-xs text-slate-600">Harbiy (maxsus) unvon</label><input v-model="form.military_rank" class="w-full rounded border px-2 py-1.5 text-sm" /></div>
          <div><label class="mb-1 block text-xs text-slate-600">Partiyaviyligi</label><input v-model="form.party_affiliation" class="w-full rounded border px-2 py-1.5 text-sm" /></div>
          <div><label class="mb-1 block text-xs text-slate-600">Telefon</label><input v-model="form.phone_number" placeholder="+998901234567" class="w-full rounded border px-2 py-1.5 text-sm" /></div>

          <div class="sm:col-span-2"><label class="mb-1 block text-xs text-slate-600">Joriy manzil</label><input v-model="form.current_address" class="w-full rounded border px-2 py-1.5 text-sm" /></div>
          <div><label class="mb-1 block text-xs text-slate-600">Doimiy manzil</label><input v-model="form.permanent_address" class="w-full rounded border px-2 py-1.5 text-sm" /></div>

          <div>
            <label class="mb-1 block text-xs text-slate-600">Lavozimi</label>
            <PositionSelect v-model="form.position_id" />
          </div>
          <div><label class="mb-1 block text-xs text-slate-600">Joriy lavozimda (sana)</label><input v-model="form.position_since" type="date" class="w-full rounded border px-2 py-1.5 text-sm" /></div>
          <div><label class="mb-1 block text-xs text-slate-600">Ishga kirgan sana</label><input v-model="form.hire_date" type="date" class="w-full rounded border px-2 py-1.5 text-sm" /></div>

          <div>
            <label class="mb-1 block text-xs text-slate-600">Ish holati</label>
            <select v-model="form.employment_status" class="w-full rounded border px-2 py-1.5 text-sm">
              <option v-for="(label, value) in EMPLOYMENT_STATUS_LABELS" :key="value" :value="value">{{ label }}</option>
            </select>
          </div>
          <div class="sm:col-span-2"><label class="mb-1 block text-xs text-slate-600">Mutaxassislik sohasi</label><input v-model="form.specialization_area" placeholder="masalan: IT" class="w-full rounded border px-2 py-1.5 text-sm" /></div>

          <div class="sm:col-span-3"><label class="mb-1 block text-xs text-slate-600">Ijobiy fazilatlari</label><textarea v-model="form.positive_traits" rows="2" class="w-full rounded border px-2 py-1.5 text-sm"></textarea></div>
          <div class="sm:col-span-3"><label class="mb-1 block text-xs text-slate-600">Salbiy fazilatlari</label><textarea v-model="form.negative_traits" rows="2" class="w-full rounded border px-2 py-1.5 text-sm"></textarea></div>
        </div>

        <p v-if="error" class="mt-3 text-sm text-red-600">{{ error }}</p>
        <button type="submit" :disabled="saving" class="mt-4 rounded bg-slate-800 px-4 py-2 text-sm text-white disabled:opacity-50">
          {{ saving ? 'Saqlanmoqda...' : "Saqlash" }}
        </button>
      </form>

      <div class="flex flex-col gap-6">
        <RelativesSection :employee-id="employeeId" :items="employee.relatives" @changed="reload" />
        <EducationSection :employee-id="employeeId" :items="employee.education_history" @changed="reload" />
        <WorkHistorySection :employee-id="employeeId" :items="employee.work_history" @changed="reload" />
        <AwardsSection :employee-id="employeeId" :items="employee.awards" @changed="reload" />
        <ForeignTripsSection :employee-id="employeeId" :items="employee.foreign_trips" @changed="reload" />
        <DocumentAttachmentsSection :employee-id="employeeId" :items="employee.attachments" @changed="reload" />
      </div>
    </template>
  </div>
</template>

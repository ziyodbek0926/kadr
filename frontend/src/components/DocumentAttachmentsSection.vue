<script setup lang="ts">
import { deleteAttachment, downloadAttachment, uploadAttachment } from '@/api/employees'
import { ATTACHMENT_TYPE_LABELS } from '@/constants/labels'
import type { DocumentAttachmentRead } from '@/types/employee'
import { ref } from 'vue'

const props = defineProps<{ employeeId: number; items: DocumentAttachmentRead[] }>()
const emit = defineEmits<{ changed: [] }>()

const showForm = ref(false)
const selectedFile = ref<File | null>(null)
const fileType = ref('diplom')
const saving = ref(false)
const error = ref('')

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  selectedFile.value = input.files?.[0] ?? null
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  return iso.slice(0, 10)
}

async function submit() {
  error.value = ''
  if (!selectedFile.value) {
    error.value = 'Faylni tanlang'
    return
  }
  saving.value = true
  try {
    await uploadAttachment(props.employeeId, selectedFile.value, fileType.value)
    selectedFile.value = null
    showForm.value = false
    emit('changed')
  } catch (e) {
    error.value = extractError(e)
  } finally {
    saving.value = false
  }
}

async function remove(attachment: DocumentAttachmentRead) {
  if (!confirm(`"${attachment.original_filename}" faylini o'chirishni tasdiqlaysizmi?`)) return
  await deleteAttachment(props.employeeId, attachment.id)
  emit('changed')
}

function extractError(e: unknown): string {
  const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
  return typeof detail === 'string' ? detail : 'Yuklashda xatolik yuz berdi'
}
</script>

<template>
  <section class="rounded-lg bg-white p-5 shadow">
    <div class="mb-3 flex items-center justify-between">
      <h2 class="text-lg font-semibold text-slate-800">Biriktirilgan hujjatlar</h2>
      <button class="text-sm text-blue-600 hover:underline" @click="showForm = !showForm">
        {{ showForm ? 'Bekor qilish' : '+ Qo\'shish' }}
      </button>
    </div>

    <table v-if="items.length" class="mb-3 w-full text-sm">
      <thead>
        <tr class="border-b text-left text-slate-500">
          <th class="p-2">Fayl nomi</th>
          <th class="p-2">Turi</th>
          <th class="p-2">Hajmi</th>
          <th class="p-2">Yuklangan sana</th>
          <th class="p-2"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id" class="border-b">
          <td class="p-2">{{ item.original_filename }}</td>
          <td class="p-2">{{ ATTACHMENT_TYPE_LABELS[item.file_type] ?? item.file_type }}</td>
          <td class="p-2">{{ formatSize(item.size_bytes) }}</td>
          <td class="p-2">{{ formatDate(item.uploaded_at) }}</td>
          <td class="p-2 text-right">
            <button class="mr-3 text-blue-600 hover:underline" @click="downloadAttachment(employeeId, item)">
              Yuklab olish
            </button>
            <button class="text-red-600 hover:underline" @click="remove(item)">O'chirish</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="mb-3 text-sm text-slate-400">Biriktirilgan hujjat yo'q.</p>

    <form v-if="showForm" class="grid grid-cols-1 gap-3 rounded border bg-slate-50 p-4 sm:grid-cols-3" @submit.prevent="submit">
      <div>
        <label class="mb-1 block text-xs text-slate-600">Hujjat turi</label>
        <select v-model="fileType" class="w-full rounded border px-2 py-1.5 text-sm">
          <option v-for="(label, value) in ATTACHMENT_TYPE_LABELS" :key="value" :value="value">{{ label }}</option>
        </select>
      </div>
      <div class="sm:col-span-2">
        <label class="mb-1 block text-xs text-slate-600">Fayl</label>
        <input
          type="file"
          accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
          class="w-full rounded border px-2 py-1.5 text-sm"
          @change="onFileChange"
        />
        <p class="mt-1 text-xs text-slate-400">Ruxsat etilgan: PDF, JPG, PNG, DOC, DOCX. Maksimal hajm: 10 MB.</p>
      </div>
      <p v-if="error" class="text-sm text-red-600 sm:col-span-3">{{ error }}</p>
      <div class="sm:col-span-3">
        <button type="submit" :disabled="saving" class="rounded bg-slate-800 px-4 py-1.5 text-sm text-white disabled:opacity-50">
          {{ saving ? 'Yuklanmoqda...' : 'Saqlash' }}
        </button>
      </div>
    </form>
  </section>
</template>

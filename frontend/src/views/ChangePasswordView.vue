<script setup lang="ts">
import { changeMyPassword } from '@/api/users'
import { isAxiosError } from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const error = ref('')
const done = ref(false)
const loading = ref(false)

const router = useRouter()

async function handleSubmit() {
  error.value = ''
  if (newPassword.value !== confirmPassword.value) {
    error.value = "Yangi parol ikkala maydonda bir xil bo'lishi kerak"
    return
  }
  loading.value = true
  try {
    await changeMyPassword(currentPassword.value, newPassword.value)
    done.value = true
  } catch (err) {
    if (isAxiosError(err) && typeof err.response?.data?.detail === 'string') {
      error.value = err.response.data.detail
    } else {
      error.value = "Parolni almashtirishda xatolik yuz berdi"
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-sm p-6">
    <button class="mb-4 text-sm text-slate-500 hover:underline" @click="router.back()">&larr; Orqaga</button>

    <div class="rounded-lg bg-white p-6 shadow">
      <h1 class="mb-4 text-xl font-semibold text-slate-800">Parolni almashtirish</h1>

      <p v-if="done" class="text-sm text-emerald-600">Parol muvaffaqiyatli almashtirildi.</p>

      <form v-else @submit.prevent="handleSubmit">
        <label class="mb-1 block text-sm text-slate-600">Joriy parol</label>
        <input
          v-model="currentPassword"
          type="password"
          required
          autocomplete="current-password"
          class="mb-4 w-full rounded border px-3 py-2"
        />

        <label class="mb-1 block text-sm text-slate-600">Yangi parol</label>
        <input
          v-model="newPassword"
          type="password"
          required
          minlength="10"
          autocomplete="new-password"
          class="w-full rounded border px-3 py-2"
        />
        <p class="mb-4 mt-1 text-xs text-slate-400">Kamida 10 belgi, katta va kichik harf, raqam bo'lishi shart</p>

        <label class="mb-1 block text-sm text-slate-600">Yangi parolni takrorlang</label>
        <input
          v-model="confirmPassword"
          type="password"
          required
          minlength="10"
          autocomplete="new-password"
          class="mb-4 w-full rounded border px-3 py-2"
        />

        <p v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded bg-slate-800 py-2 text-white hover:bg-slate-700 disabled:opacity-50"
        >
          {{ loading ? 'Saqlanmoqda...' : 'Parolni almashtirish' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { createSuperAdmin } from '@/api/setup'
import { isAxiosError } from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const fullName = ref('')
const error = ref('')
const loading = ref(false)
const done = ref(false)

const router = useRouter()

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await createSuperAdmin({ username: username.value, password: password.value, full_name: fullName.value })
    done.value = true
    setTimeout(() => router.push({ name: 'login' }), 2000)
  } catch (err) {
    if (isAxiosError(err) && typeof err.response?.data?.detail === 'string') {
      error.value = err.response.data.detail
    } else if (isAxiosError(err) && !err.response) {
      error.value = "Serverga ulanib bo'lmadi. Backend ishga tushirilganini tekshiring."
    } else {
      error.value = "Sozlashda xatolik yuz berdi"
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-slate-100">
    <div class="w-full max-w-sm rounded-lg bg-white p-8 shadow">
      <h1 class="mb-2 text-xl font-semibold text-slate-800">Kadr — birinchi sozlash</h1>
      <p class="mb-6 text-sm text-slate-500">
        Tizimda hali foydalanuvchi yo'q. Birinchi SuperAdmin hisobini shu yerda yarating.
      </p>

      <template v-if="done">
        <p class="text-sm text-emerald-600">
          Tayyor! Login sahifasiga yo'naltirilmoqdasiz&hellip;
        </p>
      </template>

      <form v-else @submit.prevent="handleSubmit">
        <label class="mb-1 block text-sm text-slate-600">F.I.Sh.</label>
        <input v-model="fullName" type="text" required minlength="2" class="mb-4 w-full rounded border px-3 py-2" />

        <label class="mb-1 block text-sm text-slate-600">Login</label>
        <input
          v-model="username"
          type="text"
          required
          minlength="3"
          autocomplete="username"
          class="mb-4 w-full rounded border px-3 py-2"
        />

        <label class="mb-1 block text-sm text-slate-600">Parol</label>
        <input
          v-model="password"
          type="password"
          required
          minlength="10"
          autocomplete="new-password"
          class="w-full rounded border px-3 py-2"
        />
        <p class="mb-4 mt-1 text-xs text-slate-400">Kamida 10 belgi, katta va kichik harf, raqam bo'lishi shart</p>

        <p v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded bg-slate-800 py-2 text-white hover:bg-slate-700 disabled:opacity-50"
        >
          {{ loading ? 'Yaratilmoqda...' : 'Hisobni yaratish' }}
        </button>
      </form>
    </div>
  </div>
</template>

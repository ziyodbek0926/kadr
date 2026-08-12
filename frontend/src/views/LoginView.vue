<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { isAxiosError } from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push({ name: 'search' })
  } catch (err) {
    if (isAxiosError(err)) {
      if (!err.response) {
        error.value = "Serverga ulanib bo'lmadi. Backend ishga tushirilganini tekshiring."
      } else if (err.response.status === 423) {
        error.value = "Hisob vaqtincha bloklangan — birozdan so'ng qayta urinib ko'ring."
      } else if (err.response.status === 429) {
        error.value = "Juda ko'p urinish qilindi. Birozdan so'ng qayta urinib ko'ring."
      } else {
        error.value = "Login yoki parol noto'g'ri"
      }
    } else {
      error.value = "Kutilmagan xatolik yuz berdi"
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-slate-100">
    <form class="w-full max-w-sm rounded-lg bg-white p-8 shadow" @submit.prevent="handleSubmit">
      <h1 class="mb-6 text-xl font-semibold text-slate-800">Kadrlar tizimiga kirish</h1>

      <label class="mb-1 block text-sm text-slate-600">Login</label>
      <input v-model="username" type="text" required autocomplete="username" class="mb-4 w-full rounded border px-3 py-2" />

      <label class="mb-1 block text-sm text-slate-600">Parol</label>
      <input
        v-model="password"
        type="password"
        required
        autocomplete="current-password"
        class="mb-4 w-full rounded border px-3 py-2"
      />

      <p v-if="error" class="mb-4 text-sm text-red-600">{{ error }}</p>

      <button
        type="submit"
        :disabled="loading"
        class="w-full rounded bg-slate-800 py-2 text-white hover:bg-slate-700 disabled:opacity-50"
      >
        {{ loading ? 'Yuklanmoqda...' : 'Kirish' }}
      </button>
    </form>
  </div>
</template>

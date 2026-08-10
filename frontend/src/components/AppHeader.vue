<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

async function logout() {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <header v-if="auth.accessToken" class="border-b bg-white">
    <div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
      <RouterLink :to="{ name: 'search' }" class="font-semibold text-slate-800">Kadr</RouterLink>
      <div class="flex items-center gap-4 text-sm text-slate-500">
        <span>{{ auth.username }}</span>
        <button class="text-slate-500 hover:text-slate-800 hover:underline" @click="logout">Chiqish</button>
      </div>
    </div>
  </header>
</template>

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
      <nav class="flex items-center gap-5">
        <RouterLink :to="{ name: 'search' }" class="font-semibold text-slate-800">Kadr</RouterLink>
        <RouterLink :to="{ name: 'search' }" class="text-sm text-slate-500 hover:text-slate-800" active-class="text-slate-800 font-medium">
          Qidiruv
        </RouterLink>
        <RouterLink :to="{ name: 'dashboard' }" class="text-sm text-slate-500 hover:text-slate-800" active-class="text-slate-800 font-medium">
          Statistika
        </RouterLink>
        <RouterLink :to="{ name: 'departments' }" class="text-sm text-slate-500 hover:text-slate-800" active-class="text-slate-800 font-medium">
          Bo'limlar
        </RouterLink>
        <RouterLink
          v-if="auth.isSuperAdmin"
          :to="{ name: 'users' }"
          class="text-sm text-slate-500 hover:text-slate-800"
          active-class="text-slate-800 font-medium"
        >
          Foydalanuvchilar
        </RouterLink>
      </nav>
      <div class="flex items-center gap-4 text-sm text-slate-500">
        <span>{{ auth.username }}</span>
        <RouterLink :to="{ name: 'change-password' }" class="hover:text-slate-800 hover:underline">
          Parolni almashtirish
        </RouterLink>
        <button class="text-slate-500 hover:text-slate-800 hover:underline" @click="logout">Chiqish</button>
      </div>
    </div>
  </header>
</template>

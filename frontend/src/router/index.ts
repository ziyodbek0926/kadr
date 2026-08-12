import { useAuthStore } from '@/stores/auth'
import { useSetupStore } from '@/stores/setup'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
    { path: '/setup', name: 'setup', component: () => import('@/views/SetupView.vue') },
    {
      path: '/',
      name: 'search',
      component: () => import('@/views/EmployeeSearchView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/employees/new',
      name: 'employee-create',
      component: () => import('@/views/EmployeeCreateView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/employees/:id',
      name: 'employee-detail',
      component: () => import('@/views/EmployeeDetailView.vue'),
      meta: { requiresAuth: true },
      props: true,
    },
    {
      path: '/departments',
      name: 'departments',
      component: () => import('@/views/DepartmentsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('@/views/UsersView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to) => {
  // Standalone o'rnatishda birinchi ishga tushirishda hech qanday foydalanuvchi yo'q —
  // shu holatni faqat bitta marta (sessiya davomida keshlab) tekshiramiz, aks holda
  // har bir navigatsiyada qo'shimcha so'rov ketardi.
  const setup = useSetupStore()
  if (setup.needsSetup === null) {
    try {
      await setup.checkStatus()
    } catch {
      // Backend hali javob bermayotgan bo'lishi mumkin (masalan standalone rejimda
      // hali ishga tushmoqda) — bu holatda setup tekshiruvini o'tkazib yuboramiz,
      // pastdagi requiresAuth tekshiruvi baribir /login'ga yo'naltiradi.
      setup.needsSetup = false
    }
  }
  if (setup.needsSetup && to.name !== 'setup') {
    return { name: 'setup' }
  }
  if (!setup.needsSetup && to.name === 'setup') {
    return { name: 'login' }
  }

  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.accessToken) {
    return { name: 'login' }
  }
})

export default router

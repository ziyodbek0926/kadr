import { useAuthStore } from '@/stores/auth';
import { createRouter, createWebHistory } from 'vue-router';
const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
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
});
router.beforeEach((to) => {
    const auth = useAuthStore();
    if (to.meta.requiresAuth && !auth.accessToken) {
        return { name: 'login' };
    }
});
export default router;

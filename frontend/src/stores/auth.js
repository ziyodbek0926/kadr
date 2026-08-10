import { defineStore } from 'pinia';
import apiClient from '@/api/client';
export const useAuthStore = defineStore('auth', {
    state: () => ({
        accessToken: null,
        username: null,
        role: null,
    }),
    actions: {
        async login(username, password) {
            const { data } = await apiClient.post('/auth/login', { username, password });
            this.accessToken = data.access_token;
            const me = await apiClient.get('/auth/me');
            this.username = me.data.username;
            this.role = me.data.role.code;
        },
        async refreshAccessToken() {
            const { data } = await apiClient.post('/auth/refresh');
            this.accessToken = data.access_token;
            return data.access_token;
        },
        async logout() {
            try {
                await apiClient.post('/auth/logout');
            }
            finally {
                this.accessToken = null;
                this.username = null;
                this.role = null;
            }
        },
    },
});

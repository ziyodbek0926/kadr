import apiClient from '@/api/client';
export async function getDashboardStats() {
    const { data } = await apiClient.get('/dashboard/stats');
    return data;
}

import apiClient from '@/api/client';
export async function listUsers() {
    const { data } = await apiClient.get('/users');
    return data;
}
export async function createUser(payload) {
    const { data } = await apiClient.post('/users', payload);
    return data;
}
export async function deactivateUser(id) {
    await apiClient.patch(`/users/${id}/deactivate`);
}

import apiClient from '@/api/client';
export async function listDepartments() {
    const { data } = await apiClient.get('/departments');
    return data;
}
export async function createDepartment(payload) {
    const { data } = await apiClient.post('/departments', payload);
    return data;
}
export async function updateDepartment(id, payload) {
    const { data } = await apiClient.patch(`/departments/${id}`, payload);
    return data;
}
export async function deleteDepartment(id) {
    await apiClient.delete(`/departments/${id}`);
}
export async function listPositions(departmentId) {
    const { data } = await apiClient.get('/positions', {
        params: departmentId ? { department_id: departmentId } : undefined,
    });
    return data;
}
export async function createPosition(payload) {
    const { data } = await apiClient.post('/positions', payload);
    return data;
}
export async function updatePosition(id, payload) {
    const { data } = await apiClient.patch(`/positions/${id}`, payload);
    return data;
}
export async function deletePosition(id) {
    await apiClient.delete(`/positions/${id}`);
}

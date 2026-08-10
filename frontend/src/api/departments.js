import apiClient from '@/api/client';
export async function listDepartments() {
    const { data } = await apiClient.get('/departments');
    return data;
}
export async function listPositions(departmentId) {
    const { data } = await apiClient.get('/positions', {
        params: departmentId ? { department_id: departmentId } : undefined,
    });
    return data;
}

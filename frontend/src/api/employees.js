import apiClient from '@/api/client';
export async function searchEmployees(filters) {
    const { data } = await apiClient.post('/employees/search', filters);
    return data;
}
export async function listEmployees(params = {}) {
    const { data } = await apiClient.get('/employees', { params });
    return data;
}
export async function getEmployee(id) {
    const { data } = await apiClient.get(`/employees/${id}`);
    return data;
}
export async function getEmployeeSensitive(id) {
    const { data } = await apiClient.get(`/employees/${id}/sensitive`);
    return data;
}
export async function createEmployee(payload) {
    const { data } = await apiClient.post('/employees', payload);
    return data;
}
export async function updateEmployee(id, payload) {
    const { data } = await apiClient.patch(`/employees/${id}`, payload);
    return data;
}
export async function deleteEmployee(id) {
    await apiClient.delete(`/employees/${id}`);
}
export async function downloadObjektivka(employeeId, fileNameHint) {
    // Oddiy <a href> ishlatilmaydi — u brauzer navigatsiyasi bo'lib, axios interceptor
    // qo'shadigan Authorization header'ini olib keta olmaydi (401 bilan tugaydi). Shu sababli
    // faylni avval autentifikatsiyalangan so'rov bilan blob sifatida olib, keyin klient
    // tomonida vaqtinchalik havola orqali yuklab olishga majburlaymiz.
    const response = await apiClient.get(`/employees/${employeeId}/objektivka`, { responseType: 'blob' });
    const url = URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${fileNameHint}.docx`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}
export async function exportEmployeesToExcel(filters, fileNameHint = 'xodimlar') {
    const response = await apiClient.post('/employees/export', filters, { responseType: 'blob' });
    const url = URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${fileNameHint}.xlsx`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}
/**
 * relatives/education/work-history/awards/foreign-trips — barchasi bir xil naqsh:
 * POST /employees/{id}/{resource}, PATCH/DELETE /employees/{id}/{resource}/{itemId}.
 * Backend'dagi app/api/v1/endpoints/employees.py bilan bir xil URL segmentlariga mos.
 */
function nestedResourceApi(resourcePath) {
    return {
        async add(employeeId, payload) {
            const { data } = await apiClient.post(`/employees/${employeeId}/${resourcePath}`, payload);
            return data;
        },
        async update(employeeId, itemId, payload) {
            const { data } = await apiClient.patch(`/employees/${employeeId}/${resourcePath}/${itemId}`, payload);
            return data;
        },
        async remove(employeeId, itemId) {
            await apiClient.delete(`/employees/${employeeId}/${resourcePath}/${itemId}`);
        },
    };
}
export const relativesApi = nestedResourceApi('relatives');
export const educationApi = nestedResourceApi('education');
export const workHistoryApi = nestedResourceApi('work-history');
export const awardsApi = nestedResourceApi('awards');
export const foreignTripsApi = nestedResourceApi('foreign-trips');
/**
 * Biriktirilgan hujjatlar ro'yxati alohida GET'ga ega emas — getEmployee()/getEmployeeDetail
 * chaqirilganda EmployeeDetailRead.attachments orqali keladi (boshqa bola-resurslar kabi).
 */
export async function uploadAttachment(employeeId, file, fileType) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);
    const { data } = await apiClient.post(`/employees/${employeeId}/attachments`, formData);
    return data;
}
export async function downloadAttachment(employeeId, attachment) {
    const response = await apiClient.get(`/employees/${employeeId}/attachments/${attachment.id}/download`, {
        responseType: 'blob',
    });
    const url = URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.download = attachment.original_filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}
export async function deleteAttachment(employeeId, attachmentId) {
    await apiClient.delete(`/employees/${employeeId}/attachments/${attachmentId}`);
}

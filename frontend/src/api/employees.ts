import apiClient from '@/api/client'
import type {
  AwardInput,
  AwardRead,
  DocumentAttachmentRead,
  EducationHistoryInput,
  EducationHistoryRead,
  EmployeeDetailRead,
  EmployeeInput,
  EmployeeListItem,
  EmployeeSearchFilter,
  EmployeeSearchResult,
  EmployeeSensitiveRead,
  ForeignTripInput,
  ForeignTripRead,
  RelativeInput,
  RelativeRead,
  WorkHistoryInput,
  WorkHistoryRead,
} from '@/types/employee'

export async function searchEmployees(filters: EmployeeSearchFilter): Promise<EmployeeSearchResult> {
  const { data } = await apiClient.post<EmployeeSearchResult>('/employees/search', filters)
  return data
}

export async function listEmployees(params: { skip?: number; limit?: number } = {}): Promise<EmployeeListItem[]> {
  const { data } = await apiClient.get<EmployeeListItem[]>('/employees', { params })
  return data
}

export async function getEmployee(id: number): Promise<EmployeeDetailRead> {
  const { data } = await apiClient.get<EmployeeDetailRead>(`/employees/${id}`)
  return data
}

export async function getEmployeeSensitive(id: number): Promise<EmployeeSensitiveRead> {
  const { data } = await apiClient.get<EmployeeSensitiveRead>(`/employees/${id}/sensitive`)
  return data
}

export async function createEmployee(payload: EmployeeInput): Promise<EmployeeDetailRead> {
  const { data } = await apiClient.post<EmployeeDetailRead>('/employees', payload)
  return data
}

export async function updateEmployee(id: number, payload: Partial<EmployeeInput>): Promise<EmployeeDetailRead> {
  const { data } = await apiClient.patch<EmployeeDetailRead>(`/employees/${id}`, payload)
  return data
}

export async function deleteEmployee(id: number): Promise<void> {
  await apiClient.delete(`/employees/${id}`)
}

export async function downloadObjektivka(employeeId: number, fileNameHint: string): Promise<void> {
  // Oddiy <a href> ishlatilmaydi — u brauzer navigatsiyasi bo'lib, axios interceptor
  // qo'shadigan Authorization header'ini olib keta olmaydi (401 bilan tugaydi). Shu sababli
  // faylni avval autentifikatsiyalangan so'rov bilan blob sifatida olib, keyin klient
  // tomonida vaqtinchalik havola orqali yuklab olishga majburlaymiz.
  const response = await apiClient.get(`/employees/${employeeId}/objektivka`, { responseType: 'blob' })
  const url = URL.createObjectURL(response.data as Blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${fileNameHint}.docx`
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

export async function exportEmployeesToExcel(filters: EmployeeSearchFilter, fileNameHint = 'xodimlar'): Promise<void> {
  const response = await apiClient.post('/employees/export', filters, { responseType: 'blob' })
  const url = URL.createObjectURL(response.data as Blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${fileNameHint}.xlsx`
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

/**
 * relatives/education/work-history/awards/foreign-trips — barchasi bir xil naqsh:
 * POST /employees/{id}/{resource}, PATCH/DELETE /employees/{id}/{resource}/{itemId}.
 * Backend'dagi app/api/v1/endpoints/employees.py bilan bir xil URL segmentlariga mos.
 */
function nestedResourceApi<TRead, TInput>(resourcePath: string) {
  return {
    async add(employeeId: number, payload: TInput): Promise<TRead> {
      const { data } = await apiClient.post<TRead>(`/employees/${employeeId}/${resourcePath}`, payload)
      return data
    },
    async update(employeeId: number, itemId: number, payload: Partial<TInput>): Promise<TRead> {
      const { data } = await apiClient.patch<TRead>(`/employees/${employeeId}/${resourcePath}/${itemId}`, payload)
      return data
    },
    async remove(employeeId: number, itemId: number): Promise<void> {
      await apiClient.delete(`/employees/${employeeId}/${resourcePath}/${itemId}`)
    },
  }
}

export const relativesApi = nestedResourceApi<RelativeRead, RelativeInput>('relatives')
export const educationApi = nestedResourceApi<EducationHistoryRead, EducationHistoryInput>('education')
export const workHistoryApi = nestedResourceApi<WorkHistoryRead, WorkHistoryInput>('work-history')
export const awardsApi = nestedResourceApi<AwardRead, AwardInput>('awards')
export const foreignTripsApi = nestedResourceApi<ForeignTripRead, ForeignTripInput>('foreign-trips')

/**
 * Biriktirilgan hujjatlar ro'yxati alohida GET'ga ega emas — getEmployee()/getEmployeeDetail
 * chaqirilganda EmployeeDetailRead.attachments orqali keladi (boshqa bola-resurslar kabi).
 */
export async function uploadAttachment(
  employeeId: number,
  file: File,
  fileType: string,
): Promise<DocumentAttachmentRead> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('file_type', fileType)
  const { data } = await apiClient.post<DocumentAttachmentRead>(`/employees/${employeeId}/attachments`, formData)
  return data
}

export async function downloadAttachment(
  employeeId: number,
  attachment: DocumentAttachmentRead,
): Promise<void> {
  const response = await apiClient.get(`/employees/${employeeId}/attachments/${attachment.id}/download`, {
    responseType: 'blob',
  })
  const url = URL.createObjectURL(response.data as Blob)
  const link = document.createElement('a')
  link.href = url
  link.download = attachment.original_filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

export async function deleteAttachment(employeeId: number, attachmentId: number): Promise<void> {
  await apiClient.delete(`/employees/${employeeId}/attachments/${attachmentId}`)
}

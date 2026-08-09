import apiClient from '@/api/client'
import type { EmployeeSearchFilter, EmployeeSearchResult } from '@/types/employee'

export async function searchEmployees(filters: EmployeeSearchFilter): Promise<EmployeeSearchResult> {
  const { data } = await apiClient.post<EmployeeSearchResult>('/employees/search', filters)
  return data
}

export async function downloadObjektivka(employeeId: number, fileNameHint: string): Promise<void> {
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

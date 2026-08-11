import apiClient from '@/api/client'
import type { DepartmentInput, DepartmentRead, PositionInput, PositionRead, PositionReadWithDepartment } from '@/types/employee'

export async function listDepartments(): Promise<DepartmentRead[]> {
  const { data } = await apiClient.get<DepartmentRead[]>('/departments')
  return data
}

export async function createDepartment(payload: DepartmentInput): Promise<DepartmentRead> {
  const { data } = await apiClient.post<DepartmentRead>('/departments', payload)
  return data
}

export async function updateDepartment(id: number, payload: Partial<DepartmentInput>): Promise<DepartmentRead> {
  const { data } = await apiClient.patch<DepartmentRead>(`/departments/${id}`, payload)
  return data
}

export async function deleteDepartment(id: number): Promise<void> {
  await apiClient.delete(`/departments/${id}`)
}

export async function listPositions(departmentId?: number): Promise<PositionReadWithDepartment[]> {
  const { data } = await apiClient.get<PositionReadWithDepartment[]>('/positions', {
    params: departmentId ? { department_id: departmentId } : undefined,
  })
  return data
}

export async function createPosition(payload: PositionInput): Promise<PositionRead> {
  const { data } = await apiClient.post<PositionRead>('/positions', payload)
  return data
}

export async function updatePosition(id: number, payload: Partial<PositionInput>): Promise<PositionRead> {
  const { data } = await apiClient.patch<PositionRead>(`/positions/${id}`, payload)
  return data
}

export async function deletePosition(id: number): Promise<void> {
  await apiClient.delete(`/positions/${id}`)
}

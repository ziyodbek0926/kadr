import apiClient from '@/api/client'
import type { DepartmentRead, PositionReadWithDepartment } from '@/types/employee'

export async function listDepartments(): Promise<DepartmentRead[]> {
  const { data } = await apiClient.get<DepartmentRead[]>('/departments')
  return data
}

export async function listPositions(departmentId?: number): Promise<PositionReadWithDepartment[]> {
  const { data } = await apiClient.get<PositionReadWithDepartment[]>('/positions', {
    params: departmentId ? { department_id: departmentId } : undefined,
  })
  return data
}

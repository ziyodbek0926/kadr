import apiClient from '@/api/client'
import type { UserCreateInput, UserRead } from '@/types/employee'

export async function listUsers(): Promise<UserRead[]> {
  const { data } = await apiClient.get<UserRead[]>('/users')
  return data
}

export async function createUser(payload: UserCreateInput): Promise<UserRead> {
  const { data } = await apiClient.post<UserRead>('/users', payload)
  return data
}

export async function deactivateUser(id: number): Promise<void> {
  await apiClient.patch(`/users/${id}/deactivate`)
}

export async function changeMyPassword(currentPassword: string, newPassword: string): Promise<void> {
  await apiClient.patch('/users/me/password', { current_password: currentPassword, new_password: newPassword })
}

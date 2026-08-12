import apiClient from '@/api/client'

export interface SetupStatus {
  needs_setup: boolean
}

export interface SuperAdminCreateInput {
  username: string
  password: string
  full_name: string
}

export async function getSetupStatus(): Promise<SetupStatus> {
  const { data } = await apiClient.get<SetupStatus>('/setup/status')
  return data
}

export async function createSuperAdmin(payload: SuperAdminCreateInput): Promise<void> {
  await apiClient.post('/setup/create-superadmin', payload)
}

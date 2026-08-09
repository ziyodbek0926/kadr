export type Gender = 'male' | 'female'
export type EmploymentStatus = 'active' | 'on_leave' | 'dismissed'
export type EducationLevel = 'secondary' | 'secondary_special' | 'bachelor' | 'master' | 'phd'

export interface PositionRead {
  id: number
  title: string
  department_id: number
  category: string | null
  is_vacant: boolean
}

export interface EmployeeListItem {
  id: number
  full_name: string
  birth_date: string
  gender: Gender
  position: PositionRead | null
  employment_status: EmploymentStatus
  specialization_area: string | null
}

export interface EmployeeSearchFilter {
  full_name?: string
  department_id?: number
  position_id?: number
  gender?: Gender
  employment_status?: EmploymentStatus
  min_age?: number
  max_age?: number
  education_level?: EducationLevel
  specialty_keyword?: string
  specialization_area?: string
  min_years_in_position?: number
  nationality?: string
  has_awards?: boolean
  hired_after?: string
  hired_before?: string
  page?: number
  page_size?: number
}

export interface EmployeeSearchResult {
  total: number
  page: number
  page_size: number
  items: EmployeeListItem[]
}

export type Gender = 'male' | 'female'
export type EmploymentStatus = 'active' | 'on_leave' | 'dismissed'
export type EducationLevel = 'secondary' | 'secondary_special' | 'bachelor' | 'master' | 'phd'
export type MaritalStatus = 'single' | 'married' | 'divorced' | 'widowed'
export type RelativeType = 'father' | 'mother' | 'spouse' | 'child' | 'sibling' | 'other'

export interface DepartmentRead {
  id: number
  name: string
  parent_id: number | null
}
export type DepartmentInput = Omit<DepartmentRead, 'id'>

export interface PositionRead {
  id: number
  title: string
  department_id: number
  category: string | null
  is_vacant: boolean
}
export interface PositionReadWithDepartment extends PositionRead {
  department: DepartmentRead
}
export type PositionInput = Omit<PositionRead, 'id'>

export interface RelativeRead {
  id: number
  employee_id: number
  relation_type: RelativeType
  full_name: string
  birth_year: number | null
  birth_place: string | null
  workplace: string | null
  position_title: string | null
  address: string | null
}
export type RelativeInput = Omit<RelativeRead, 'id' | 'employee_id'>

export interface EducationHistoryRead {
  id: number
  employee_id: number
  institution_name: string
  specialty: string | null
  level: EducationLevel
  start_date: string | null
  end_date: string | null
  document_number: string | null
}
export type EducationHistoryInput = Omit<EducationHistoryRead, 'id' | 'employee_id'>

export interface WorkHistoryRead {
  id: number
  employee_id: number
  organization_name: string
  position_title: string
  start_date: string
  end_date: string | null
  order_reference: string | null
  notes: string | null
}
export type WorkHistoryInput = Omit<WorkHistoryRead, 'id' | 'employee_id'>

export interface AwardRead {
  id: number
  employee_id: number
  name: string
  awarded_date: string
  recommending_organization: string | null
}
export type AwardInput = Omit<AwardRead, 'id' | 'employee_id'>

export interface ForeignTripRead {
  id: number
  employee_id: number
  country: string
  purpose: string | null
  start_date: string
  end_date: string | null
  order_basis: string | null
}
export type ForeignTripInput = Omit<ForeignTripRead, 'id' | 'employee_id'>

export interface EmployeeListItem {
  id: number
  full_name: string
  birth_date: string
  gender: Gender
  position: PositionRead | null
  employment_status: EmploymentStatus
  specialization_area: string | null
}

export interface EmployeeRead extends EmployeeListItem {
  last_name: string
  first_name: string
  middle_name: string | null
  birth_place: string | null
  nationality: string | null
  citizenship: string | null
  marital_status: MaritalStatus | null
  academic_degree: string | null
  academic_title: string | null
  foreign_languages: string | null
  military_rank: string | null
  party_affiliation: string | null
  public_office_note: string | null
  passport_series: string | null
  passport_issued_by: string | null
  passport_issued_date: string | null
  current_address: string | null
  permanent_address: string | null
  phone_number: string | null
  photo_path: string | null
  position_since: string | null
  hire_date: string | null
  termination_date: string | null
  positive_traits: string | null
  negative_traits: string | null
  created_at: string
  updated_at: string
}

export interface EmployeeDetailRead extends EmployeeRead {
  relatives: RelativeRead[]
  education_history: EducationHistoryRead[]
  work_history: WorkHistoryRead[]
  awards: AwardRead[]
  foreign_trips: ForeignTripRead[]
}

export interface EmployeeSensitiveRead {
  pinfl: string | null
  passport_number: string | null
}

// Backend'dagi app.schemas.employee.EmployeeBase bilan mos (Create va Update ikkalasi
// uchun ham ishlatiladi — Update'da barcha maydonlar amalda ixtiyoriy).
export interface EmployeeInput {
  last_name: string
  first_name: string
  middle_name?: string | null
  birth_date: string
  birth_place?: string | null
  gender: Gender
  nationality?: string | null
  citizenship?: string | null
  marital_status?: MaritalStatus | null
  academic_degree?: string | null
  academic_title?: string | null
  foreign_languages?: string | null
  military_rank?: string | null
  party_affiliation?: string | null
  public_office_note?: string | null
  pinfl?: string | null
  passport_series?: string | null
  passport_number?: string | null
  passport_issued_by?: string | null
  passport_issued_date?: string | null
  current_address?: string | null
  permanent_address?: string | null
  phone_number?: string | null
  photo_path?: string | null
  position_id?: number | null
  position_since?: string | null
  hire_date?: string | null
  employment_status?: EmploymentStatus
  termination_date?: string | null
  specialization_area?: string | null
  positive_traits?: string | null
  negative_traits?: string | null
}

// Backend'dagi app.schemas.search.EmployeeSearchFilter bilan mos — maydon nomlari va
// turlari ataylab bir xil ushlab turiladi, aks holda backend 422 (extra="forbid") qaytaradi.
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

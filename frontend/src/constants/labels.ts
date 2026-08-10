import type { EducationLevel, EmploymentStatus, Gender, MaritalStatus, RelativeType } from '@/types/employee'

export const GENDER_LABELS: Record<Gender, string> = {
  male: 'Erkak',
  female: 'Ayol',
}

export const EMPLOYMENT_STATUS_LABELS: Record<EmploymentStatus, string> = {
  active: 'Faoliyat yuritmoqda',
  on_leave: "Ta'til/dam olishda",
  dismissed: "Bo'shatilgan",
}

export const MARITAL_STATUS_LABELS: Record<MaritalStatus, string> = {
  single: "Turmush qurmagan",
  married: "Turmush qurgan",
  divorced: "Ajrashgan",
  widowed: "Beva/bev",
}

export const RELATIVE_TYPE_LABELS: Record<RelativeType, string> = {
  father: 'Otasi',
  mother: 'Onasi',
  spouse: "Turmush o'rtog'i",
  child: 'Farzandi',
  sibling: 'Aka/uka, opa/singlisi',
  other: 'Boshqa qarindosh',
}

export const EDUCATION_LEVEL_LABELS: Record<EducationLevel, string> = {
  secondary: "O'rta",
  secondary_special: "O'rta-maxsus",
  bachelor: 'Bakalavr',
  master: 'Magistr',
  phd: "Fan doktori/nomzodi",
}

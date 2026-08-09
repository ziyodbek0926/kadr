import enum


class Gender(enum.StrEnum):
    MALE = "male"
    FEMALE = "female"


class EmploymentStatus(enum.StrEnum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    DISMISSED = "dismissed"


class MaritalStatus(enum.StrEnum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class RelativeType(enum.StrEnum):
    FATHER = "father"
    MOTHER = "mother"
    SPOUSE = "spouse"
    CHILD = "child"
    SIBLING = "sibling"
    OTHER = "other"


class EducationLevel(enum.StrEnum):
    SECONDARY = "secondary"
    SECONDARY_SPECIAL = "secondary_special"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"


class UserRole(enum.StrEnum):
    SUPER_ADMIN = "super_admin"
    HR_OPERATOR = "hr_operator"
    MANAGEMENT_VIEWER = "management_viewer"
    IT_ADMIN = "it_admin"


class AuditAction(enum.StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

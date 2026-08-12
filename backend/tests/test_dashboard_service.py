from datetime import date

from app.models.enums import EducationLevel
from app.services.dashboard_service import age_bucket, highest_education_level


def test_highest_education_level_picks_max_of_several() -> None:
    levels = [EducationLevel.BACHELOR, EducationLevel.SECONDARY, EducationLevel.MASTER]
    assert highest_education_level(levels) == EducationLevel.MASTER


def test_highest_education_level_empty_returns_none() -> None:
    assert highest_education_level([]) is None


def test_highest_education_level_single_value() -> None:
    assert highest_education_level([EducationLevel.PHD]) == EducationLevel.PHD


def test_age_bucket_boundaries() -> None:
    today = date(2026, 8, 11)
    assert age_bucket(date(2000, 8, 12), today) == "<30"  
    assert age_bucket(date(1996, 8, 11), today) == "30-39"  
    assert age_bucket(date(1996, 8, 12), today) == "<30"  
    assert age_bucket(date(1966, 1, 1), today) == "60+"


def test_age_bucket_covers_middle_ranges() -> None:
    today = date(2026, 8, 11)
    assert age_bucket(date(1990, 1, 1), today) == "30-39"
    assert age_bucket(date(1980, 1, 1), today) == "40-49"
    assert age_bucket(date(1970, 1, 1), today) == "50-59"

"""설정 데이터 JSON 파일 저장소."""

import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "settings.json"

DEFAULT_SETTINGS = {
    "apply_year": 2026,
    # 최저임금
    "minimum_wage": 10320,
    "minimum_wage_update": "매년 1월",
    # 국민연금
    "national_pension_rate": 0.045,
    "national_pension_floor": 370000,
    "national_pension_cap": 5900000,
    "national_pension_update": "요율: 비정기 / 상·하한: 매년 7월",
    # 건강보험
    "health_insurance_rate": 0.03545,
    "health_insurance_update": "매년 1월",
    # 장기요양보험
    "long_term_care_rate": 0.1281,
    "long_term_care_update": "매년 1월",
    # 고용보험
    "employment_insurance_employee": 0.009,
    "employment_insurance_employer": 0.009,
    "employment_insurance_update": "비정기",
    # 산재보험
    "industrial_accident_rate": 0.007,
    "industrial_accident_update": "매년 1월 (업종별)",
    # 비과세 한도
    "meal_nontax_limit": 200000,
    "fuel_nontax_limit": 200000,
    "childcare_nontax_limit": 100000,
    "nontax_update": "소득세법 개정 시",
}


def seed_defaults_if_empty() -> None:
    """설정 파일이 없으면 기본값을 생성한다."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        save_settings(DEFAULT_SETTINGS)


def load_settings() -> dict:
    """설정을 반환한다."""
    if not DATA_FILE.exists():
        seed_defaults_if_empty()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(settings: dict) -> None:
    """설정을 JSON 파일에 저장한다."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def update_settings(data: dict) -> dict:
    """설정을 업데이트한다."""
    current = load_settings()
    current.update(data)
    save_settings(current)
    return current


def reset_settings() -> dict:
    """설정을 기본값으로 초기화한다."""
    save_settings(DEFAULT_SETTINGS)
    return DEFAULT_SETTINGS

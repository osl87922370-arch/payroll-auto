"""급여 자동정산 계산 모듈

설정 파일(settings.json)의 요율을 사용합니다.
관리자 설정 페이지에서 매년 요율을 업데이트할 수 있습니다.
"""

from dataclasses import dataclass

from app.services.settings_store import load_settings
from app.services.tax_calculator import calculate_income_tax


@dataclass
class InsuranceBreakdown:
    """개별 보험 항목의 사업주/근로자 부담금."""
    employer: int
    employee: int


@dataclass
class AllowanceResult:
    """수당 과세/비과세 분류 결과."""
    weekly_holiday: int
    monthly_leave: int
    overtime: int
    holiday_work: int
    night_work: int
    position: int
    bonus: int
    family: int
    tenure: int
    other_taxable: int
    meal_taxable: int
    meal_nontaxable: int
    fuel_taxable: int
    fuel_nontaxable: int
    childcare_taxable: int
    childcare_nontaxable: int
    other_nontaxable: int
    total_taxable: int
    total_nontaxable: int


@dataclass
class TaxResult:
    """소득세·주민세 결과."""
    income_tax: int
    resident_tax: int
    total_tax: int


@dataclass
class PayrollResult:
    """급여 정산 결과."""
    base_salary: int
    dependents: int
    allowances: AllowanceResult
    taxable_income: int
    nontaxable_income: int
    total_pay: int
    national_pension: InsuranceBreakdown
    health_insurance: InsuranceBreakdown
    long_term_care: InsuranceBreakdown
    employment_insurance: InsuranceBreakdown
    industrial_accident: InsuranceBreakdown
    retirement_provision: int
    total_employer: int
    total_employee: int
    tax: TaxResult
    total_deduction: int
    net_pay: int


def _round_to_ten(value: float) -> int:
    """10원 단위 반올림 (4대 보험 관행)."""
    return round(value / 10) * 10


def _split_nontaxable(amount: int, limit: int) -> tuple[int, int]:
    """비과세 한도를 적용하여 (과세분, 비과세분) 튜플을 반환한다."""
    nontaxable = min(amount, limit)
    taxable = amount - nontaxable
    return taxable, nontaxable


def calculate_payroll(
    base_salary: int,
    weekly_holiday: int = 0,
    monthly_leave: int = 0,
    overtime: int = 0,
    holiday_work: int = 0,
    night_work: int = 0,
    position: int = 0,
    bonus: int = 0,
    family: int = 0,
    tenure: int = 0,
    other_taxable: int = 0,
    meal: int = 0,
    fuel: int = 0,
    childcare: int = 0,
    other_nontaxable: int = 0,
    dependents: int = 1,
    settings: dict | None = None,
) -> PayrollResult:
    if base_salary < 0:
        raise ValueError("급여는 0 이상이어야 합니다.")

    # ── 설정 로드 ────────────────────────────────────────
    s = settings if settings is not None else load_settings()

    np_rate = s.get("national_pension_rate", 0.045)
    np_floor = s.get("national_pension_floor", 370_000)
    np_cap = s.get("national_pension_cap", 5_900_000)
    hi_rate = s.get("health_insurance_rate", 0.03545)
    ltc_rate = s.get("long_term_care_rate", 0.1281)
    ei_employee_rate = s.get("employment_insurance_employee", 0.009)
    ei_employer_rate = s.get("employment_insurance_employer", 0.009)
    ia_rate = s.get("industrial_accident_rate", 0.007)
    meal_limit = s.get("meal_nontax_limit", 200_000)
    fuel_limit = s.get("fuel_nontax_limit", 200_000)
    childcare_limit = s.get("childcare_nontax_limit", 100_000)

    # ── 수당 과세/비과세 분류 ────────────────────────────────
    meal_taxable, meal_nontaxable = _split_nontaxable(meal, meal_limit)
    fuel_taxable, fuel_nontaxable = _split_nontaxable(fuel, fuel_limit)
    childcare_taxable, childcare_nontaxable = _split_nontaxable(childcare, childcare_limit)

    total_taxable_allowance = (
        weekly_holiday + monthly_leave + overtime + holiday_work + night_work
        + position + bonus + family + tenure + other_taxable
        + meal_taxable + fuel_taxable + childcare_taxable
    )
    total_nontaxable_allowance = meal_nontaxable + fuel_nontaxable + childcare_nontaxable + other_nontaxable

    allowances = AllowanceResult(
        weekly_holiday=weekly_holiday,
        monthly_leave=monthly_leave,
        overtime=overtime,
        holiday_work=holiday_work,
        night_work=night_work,
        position=position,
        bonus=bonus,
        family=family,
        tenure=tenure,
        other_taxable=other_taxable,
        meal_taxable=meal_taxable,
        meal_nontaxable=meal_nontaxable,
        fuel_taxable=fuel_taxable,
        fuel_nontaxable=fuel_nontaxable,
        childcare_taxable=childcare_taxable,
        childcare_nontaxable=childcare_nontaxable,
        other_nontaxable=other_nontaxable,
        total_taxable=total_taxable_allowance,
        total_nontaxable=total_nontaxable_allowance,
    )

    # ── 과세 소득 (4대 보험 산정 기준) ──────────────────────
    taxable_income = base_salary + total_taxable_allowance
    nontaxable_income = total_nontaxable_allowance
    total_pay = taxable_income + nontaxable_income

    # ── 국민연금 (상·하한 적용) ───────────────────────────
    np_base = max(np_floor, min(taxable_income, np_cap))
    np_employee = _round_to_ten(np_base * np_rate)
    np_employer = np_employee

    # ── 건강보험 ──────────────────────────────────────────
    hi_employee = _round_to_ten(taxable_income * hi_rate)
    hi_employer = hi_employee

    # ── 장기요양보험 (건강보험료 기반) ────────────────────
    ltc_employee = _round_to_ten(hi_employee * ltc_rate)
    ltc_employer = ltc_employee

    # ── 고용보험 ──────────────────────────────────────────
    ei_employee = _round_to_ten(taxable_income * ei_employee_rate)
    ei_employer = _round_to_ten(taxable_income * ei_employer_rate)

    # ── 산재보험 (사업주 전액 부담) ───────────────────────
    ia_employer = _round_to_ten(taxable_income * ia_rate)
    ia_employee = 0

    # ── 퇴직충당금 (과세 소득의 1/12) ─────────────────────
    retirement_provision = _round_to_ten(taxable_income / 12)

    # ── 합계 ──────────────────────────────────────────────
    total_employer = (
        np_employer + hi_employer + ltc_employer + ei_employer + ia_employer + retirement_provision
    )
    total_employee = np_employee + hi_employee + ltc_employee + ei_employee

    # ── 소득세·주민세 ────────────────────────────────────
    tax_info = calculate_income_tax(taxable_income, dependents)
    tax = TaxResult(
        income_tax=tax_info["income_tax"],
        resident_tax=tax_info["resident_tax"],
        total_tax=tax_info["total_tax"],
    )

    # ── 총 공제액 (4대 보험 + 세금) ─────────────────────
    total_deduction = total_employee + tax.total_tax

    # ── 실수령액 ──────────────────────────────────────────
    net_pay = total_pay - total_deduction

    return PayrollResult(
        base_salary=base_salary,
        dependents=dependents,
        allowances=allowances,
        taxable_income=taxable_income,
        nontaxable_income=nontaxable_income,
        total_pay=total_pay,
        national_pension=InsuranceBreakdown(employer=np_employer, employee=np_employee),
        health_insurance=InsuranceBreakdown(employer=hi_employer, employee=hi_employee),
        long_term_care=InsuranceBreakdown(employer=ltc_employer, employee=ltc_employee),
        employment_insurance=InsuranceBreakdown(employer=ei_employer, employee=ei_employee),
        industrial_accident=InsuranceBreakdown(employer=ia_employer, employee=ia_employee),
        retirement_provision=retirement_provision,
        total_employer=total_employer,
        total_employee=total_employee,
        tax=tax,
        total_deduction=total_deduction,
        net_pay=net_pay,
    )

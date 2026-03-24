from dataclasses import asdict

from fastapi import APIRouter

from app.schemas.payroll import PayrollRequest, PayrollResponse
from app.services.calculator import calculate_payroll

router = APIRouter()


@router.post("/calculate", response_model=PayrollResponse)
def calculate(request: PayrollRequest):
    """기본급과 수당을 입력받아 4대 보험, 소득세, 퇴직충당금을 계산합니다."""
    a = request.allowances
    result = calculate_payroll(
        base_salary=request.base_salary,
        weekly_holiday=a.weekly_holiday,
        monthly_leave=a.monthly_leave,
        overtime=a.overtime,
        holiday_work=a.holiday_work,
        night_work=a.night_work,
        position=a.position,
        bonus=a.bonus,
        family=a.family,
        tenure=a.tenure,
        other_taxable=a.other_taxable,
        meal=a.meal,
        fuel=a.fuel,
        childcare=a.childcare,
        other_nontaxable=a.other_nontaxable,
        dependents=request.dependents,
    )
    return PayrollResponse(
        base_salary=result.base_salary,
        dependents=result.dependents,
        allowances=asdict(result.allowances),
        taxable_income=result.taxable_income,
        nontaxable_income=result.nontaxable_income,
        total_pay=result.total_pay,
        national_pension=asdict(result.national_pension),
        health_insurance=asdict(result.health_insurance),
        long_term_care=asdict(result.long_term_care),
        employment_insurance=asdict(result.employment_insurance),
        industrial_accident=asdict(result.industrial_accident),
        retirement_provision=result.retirement_provision,
        total_employer=result.total_employer,
        total_employee=result.total_employee,
        tax=asdict(result.tax),
        total_deduction=result.total_deduction,
        net_pay=result.net_pay,
    )

from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from app.schemas.employee import (
    Employee,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeePayrollResult,
    BatchPayrollResponse,
)
from app.services import employee_store
from app.services.calculator import calculate_payroll

router = APIRouter()


def _calc_for_employee(emp: dict) -> EmployeePayrollResult:
    """직원 1명의 급여를 계산하여 EmployeePayrollResult를 반환한다."""
    a = emp.get("allowances", {})
    result = calculate_payroll(
        base_salary=emp["base_salary"],
        weekly_holiday=a.get("weekly_holiday", 0),
        monthly_leave=a.get("monthly_leave", 0),
        overtime=a.get("overtime", 0),
        holiday_work=a.get("holiday_work", 0),
        night_work=a.get("night_work", 0),
        position=a.get("position", 0),
        bonus=a.get("bonus", 0),
        family=a.get("family", 0),
        tenure=a.get("tenure", 0),
        other_taxable=a.get("other_taxable", 0),
        meal=a.get("meal", 0),
        fuel=a.get("fuel", 0),
        childcare=a.get("childcare", 0),
        other_nontaxable=a.get("other_nontaxable", 0),
        dependents=emp.get("dependents", 1),
    )
    return EmployeePayrollResult(
        employee_id=emp["id"],
        employee_name=emp["name"],
        employee_role=emp["role"],
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


@router.get("/", response_model=list[Employee])
def list_employees():
    """전체 직원 목록을 반환합니다."""
    return employee_store.load_employees()


@router.post("/", response_model=Employee)
def create_employee(data: EmployeeCreate):
    """새 직원을 추가합니다."""
    emp = employee_store.add_employee(name=data.name, role=data.role)
    return emp


@router.delete("/{employee_id}")
def delete_employee(employee_id: str):
    """직원을 삭제합니다."""
    deleted = employee_store.delete_employee(employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="직원을 찾을 수 없습니다.")
    return {"message": "삭제되었습니다."}


@router.get("/{employee_id}", response_model=Employee)
def get_employee(employee_id: str):
    """특정 직원 정보를 반환합니다."""
    emp = employee_store.get_employee(employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="직원을 찾을 수 없습니다.")
    return emp


@router.put("/{employee_id}", response_model=Employee)
def update_employee(employee_id: str, data: EmployeeUpdate):
    """직원의 급여/수당 정보를 업데이트합니다."""
    emp = employee_store.update_employee(employee_id, data.model_dump())
    if emp is None:
        raise HTTPException(status_code=404, detail="직원을 찾을 수 없습니다.")
    return emp


@router.get("/{employee_id}/statement", response_model=EmployeePayrollResult)
def get_statement(employee_id: str):
    """특정 직원의 급여 명세서 데이터를 반환합니다."""
    emp = employee_store.get_employee(employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="직원을 찾을 수 없습니다.")
    if emp["base_salary"] <= 0:
        raise HTTPException(status_code=400, detail="기본급이 설정되지 않았습니다.")
    return _calc_for_employee(emp)


@router.post("/calculate-all", response_model=BatchPayrollResponse)
def calculate_all():
    """전체 직원의 급여를 일괄 계산합니다."""
    employees = employee_store.load_employees()
    results = []
    for emp in employees:
        if emp["base_salary"] > 0:
            results.append(_calc_for_employee(emp))

    return BatchPayrollResponse(
        results=results,
        total_pay_sum=sum(r.total_pay for r in results),
        total_employer_sum=sum(r.total_employer for r in results),
        total_employee_sum=sum(r.total_employee for r in results),
        total_net_pay_sum=sum(r.net_pay for r in results),
    )

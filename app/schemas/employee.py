from pydantic import BaseModel, Field

from app.schemas.payroll import AllowanceInput, AllowanceBreakdown, InsuranceDetail, TaxDetail


class Employee(BaseModel):
    id: str = Field(description="직원 고유 ID")
    name: str = Field(description="직원 이름")
    role: str = Field(description="직책/역할")
    base_salary: int = Field(0, ge=0, description="기본급")
    dependents: int = Field(1, ge=1, description="부양가족 수")
    allowances: AllowanceInput = Field(default_factory=AllowanceInput)


class EmployeeCreate(BaseModel):
    name: str = Field("", description="직원 이름")
    role: str = Field("", description="직책/역할")


class EmployeeUpdate(BaseModel):
    name: str | None = Field(None, description="직원 이름")
    role: str | None = Field(None, description="직책/역할")
    base_salary: int = Field(..., gt=0, description="기본급")
    dependents: int = Field(1, ge=1, description="부양가족 수")
    allowances: AllowanceInput = Field(default_factory=AllowanceInput)


class EmployeePayrollResult(BaseModel):
    employee_id: str
    employee_name: str
    employee_role: str
    base_salary: int
    dependents: int
    allowances: AllowanceBreakdown
    taxable_income: int
    nontaxable_income: int
    total_pay: int
    national_pension: InsuranceDetail
    health_insurance: InsuranceDetail
    long_term_care: InsuranceDetail
    employment_insurance: InsuranceDetail
    industrial_accident: InsuranceDetail
    retirement_provision: int
    total_employer: int
    total_employee: int
    tax: TaxDetail
    total_deduction: int
    net_pay: int


class BatchPayrollResponse(BaseModel):
    results: list[EmployeePayrollResult]
    total_pay_sum: int
    total_employer_sum: int
    total_employee_sum: int
    total_net_pay_sum: int

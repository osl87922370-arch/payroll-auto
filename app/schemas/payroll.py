from pydantic import BaseModel, Field


class AllowanceInput(BaseModel):
    # 과세 수당
    weekly_holiday: int = Field(0, ge=0, description="주휴수당 (과세)")
    monthly_leave: int = Field(0, ge=0, description="월차수당 (과세)")
    overtime: int = Field(0, ge=0, description="연장근로수당 (과세)")
    holiday_work: int = Field(0, ge=0, description="휴일근로수당 (과세)")
    night_work: int = Field(0, ge=0, description="야간근로수당 (과세)")
    position: int = Field(0, ge=0, description="직책수당 (과세)")
    bonus: int = Field(0, ge=0, description="상여금 (과세)")
    family: int = Field(0, ge=0, description="가족수당 (과세)")
    tenure: int = Field(0, ge=0, description="근속수당 (과세)")
    other_taxable: int = Field(0, ge=0, description="기타 과세 수당")
    # 비과세 수당
    meal: int = Field(0, ge=0, description="식대 (월 20만원 이하 비과세)")
    fuel: int = Field(0, ge=0, description="유류대/자가운전보조금 (월 20만원 이하 비과세)")
    childcare: int = Field(0, ge=0, description="육아수당 (월 10만원 이하 비과세)")
    other_nontaxable: int = Field(0, ge=0, description="기타 비과세 수당")


class PayrollRequest(BaseModel):
    base_salary: int = Field(..., gt=0, description="기본급 (원)")
    dependents: int = Field(1, ge=1, description="부양가족 수 (본인 포함)")
    allowances: AllowanceInput = Field(default_factory=AllowanceInput, description="수당 항목")


class InsuranceDetail(BaseModel):
    employer: int = Field(description="사업주 부담금")
    employee: int = Field(description="근로자 부담금")


class TaxDetail(BaseModel):
    income_tax: int = Field(description="소득세")
    resident_tax: int = Field(description="주민세")
    total_tax: int = Field(description="세금 합계")


class AllowanceBreakdown(BaseModel):
    # 과세 수당 상세
    weekly_holiday: int = Field(description="주휴수당")
    monthly_leave: int = Field(description="월차수당")
    overtime: int = Field(description="연장근로수당")
    holiday_work: int = Field(description="휴일근로수당")
    night_work: int = Field(description="야간근로수당")
    position: int = Field(description="직책수당")
    bonus: int = Field(description="상여금")
    family: int = Field(description="가족수당")
    tenure: int = Field(description="근속수당")
    other_taxable: int = Field(description="기타 과세 수당")
    # 비과세 수당 상세
    meal_taxable: int = Field(description="식대 과세분")
    meal_nontaxable: int = Field(description="식대 비과세분")
    fuel_taxable: int = Field(description="유류대 과세분")
    fuel_nontaxable: int = Field(description="유류대 비과세분")
    childcare_taxable: int = Field(description="육아수당 과세분")
    childcare_nontaxable: int = Field(description="육아수당 비과세분")
    other_nontaxable: int = Field(description="기타 비과세 수당")
    total_taxable: int = Field(description="과세 수당 합계")
    total_nontaxable: int = Field(description="비과세 수당 합계")


class PayrollResponse(BaseModel):
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

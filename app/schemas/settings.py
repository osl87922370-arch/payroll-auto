from pydantic import BaseModel, Field


class RateSettings(BaseModel):
    # 최저임금
    minimum_wage: int = Field(10030, gt=0, description="최저시급 (원)")
    minimum_wage_update: str = Field("매년 1월", description="변경 시기")

    # 국민연금
    national_pension_rate: float = Field(0.045, gt=0, description="국민연금 요율 (각)")
    national_pension_floor: int = Field(370000, ge=0, description="국민연금 하한액 (월)")
    national_pension_cap: int = Field(5900000, gt=0, description="국민연금 상한액 (월)")
    national_pension_update: str = Field("요율: 비정기 / 상·하한: 매년 7월", description="변경 시기")

    # 건강보험
    health_insurance_rate: float = Field(0.03545, gt=0, description="건강보험 요율 (각)")
    health_insurance_update: str = Field("매년 1월", description="변경 시기")

    # 장기요양보험
    long_term_care_rate: float = Field(0.1281, gt=0, description="장기요양보험 요율 (건강보험료 대비)")
    long_term_care_update: str = Field("매년 1월", description="변경 시기")

    # 고용보험
    employment_insurance_employee: float = Field(0.009, gt=0, description="고용보험 근로자 요율")
    employment_insurance_employer: float = Field(0.009, gt=0, description="고용보험 사업주 요율")
    employment_insurance_update: str = Field("비정기", description="변경 시기")

    # 산재보험
    industrial_accident_rate: float = Field(0.007, gt=0, description="산재보험 요율 (업종 평균)")
    industrial_accident_update: str = Field("매년 1월 (업종별)", description="변경 시기")

    # 비과세 한도
    meal_nontax_limit: int = Field(200000, ge=0, description="식대 비과세 한도 (월)")
    fuel_nontax_limit: int = Field(200000, ge=0, description="유류대 비과세 한도 (월)")
    childcare_nontax_limit: int = Field(100000, ge=0, description="육아수당 비과세 한도 (월)")
    nontax_update: str = Field("소득세법 개정 시", description="변경 시기")

    # 적용 연도
    apply_year: int = Field(2025, description="적용 연도")

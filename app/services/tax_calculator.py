"""근로소득세 계산 모듈

2025년 기준 근로소득 간이세액표 산출 공식을 사용합니다.
월 과세 소득과 부양가족 수를 기반으로 소득세·주민세를 계산합니다.
"""


def _earned_income_deduction(annual_gross: int) -> int:
    """근로소득공제 (2025년 기준)."""
    if annual_gross <= 5_000_000:
        return int(annual_gross * 0.70)
    elif annual_gross <= 15_000_000:
        return 3_500_000 + int((annual_gross - 5_000_000) * 0.40)
    elif annual_gross <= 45_000_000:
        return 7_500_000 + int((annual_gross - 15_000_000) * 0.15)
    elif annual_gross <= 100_000_000:
        return 12_000_000 + int((annual_gross - 45_000_000) * 0.05)
    else:
        return 14_750_000 + int((annual_gross - 100_000_000) * 0.02)


def _calc_tax_by_bracket(taxable_income: int) -> int:
    """종합소득세 산출세액 (2025년 기준 세율)."""
    if taxable_income <= 0:
        return 0

    brackets = [
        (14_000_000, 0.06, 0),
        (50_000_000, 0.15, 840_000),
        (88_000_000, 0.24, 6_240_000),
        (150_000_000, 0.35, 15_360_000),
        (300_000_000, 0.38, 37_060_000),
        (500_000_000, 0.40, 94_060_000),
        (1_000_000_000, 0.42, 174_060_000),
        (float('inf'), 0.45, 384_060_000),
    ]

    for limit, rate, cumulative in brackets:
        if taxable_income <= limit:
            prev_limit = 0
            for i, (l, r, c) in enumerate(brackets):
                if l == limit:
                    prev_limit = brackets[i - 1][0] if i > 0 else 0
                    break
            return cumulative + int((taxable_income - prev_limit) * rate)

    return 0


def calculate_income_tax(monthly_taxable: int, dependents: int = 1) -> dict:
    """월 과세 소득과 부양가족 수로 소득세·주민세를 계산한다.

    Args:
        monthly_taxable: 월 과세 소득 (원)
        dependents: 부양가족 수 (본인 포함, 최소 1)

    Returns:
        {"income_tax": int, "resident_tax": int, "total_tax": int}
    """
    if monthly_taxable <= 0:
        return {"income_tax": 0, "resident_tax": 0, "total_tax": 0}

    dependents = max(1, dependents)

    # 연간 총급여
    annual_gross = monthly_taxable * 12

    # 근로소득공제
    earned_deduction = _earned_income_deduction(annual_gross)

    # 근로소득금액
    earned_income = annual_gross - earned_deduction

    # 인적공제 (1인당 150만원)
    personal_deduction = dependents * 1_500_000

    # 국민연금 공제 (연간, 근로자 부담분 추정: 과세소득 × 4.5%)
    np_deduction = min(int(annual_gross * 0.045), 5_900_000 * 12 * 0.045)

    # 건강보험+장기요양 공제 추정
    hi_deduction = int(annual_gross * 0.03545)
    ltc_deduction = int(hi_deduction * 0.1281)

    # 고용보험 공제
    ei_deduction = int(annual_gross * 0.009)

    # 보험료 공제 합계
    insurance_deduction = int(np_deduction + hi_deduction + ltc_deduction + ei_deduction)

    # 표준세액공제 (특별소득공제 미적용 시 13만원)
    standard_deduction = 130_000

    # 과세표준
    taxable_base = earned_income - personal_deduction - insurance_deduction - standard_deduction
    if taxable_base <= 0:
        return {"income_tax": 0, "resident_tax": 0, "total_tax": 0}

    # 산출세액
    annual_tax = _calc_tax_by_bracket(taxable_base)

    # 근로소득세액공제
    if annual_tax <= 1_300_000:
        tax_credit = int(annual_tax * 0.55)
    else:
        tax_credit = 715_000 + int((annual_tax - 1_300_000) * 0.30)

    # 최종 연간 세액
    final_annual_tax = max(0, annual_tax - tax_credit)

    # 월 소득세 (10원 단위 절사)
    monthly_income_tax = (final_annual_tax // 12 // 10) * 10

    # 주민세 = 소득세의 10%
    monthly_resident_tax = (monthly_income_tax * 10 // 100 // 10) * 10

    return {
        "income_tax": monthly_income_tax,
        "resident_tax": monthly_resident_tax,
        "total_tax": monthly_income_tax + monthly_resident_tax,
    }

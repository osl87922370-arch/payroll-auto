from fastapi.testclient import TestClient

from app.main import app
from app.services.calculator import calculate_payroll
from app.services.settings_store import DEFAULT_SETTINGS

client = TestClient(app)

# 테스트에서 settings를 직접 주입 (파일 의존 제거)
TEST_SETTINGS = dict(DEFAULT_SETTINGS)


class TestCalculator:
    """calculator.py 단위 테스트"""

    def test_basic_salary(self):
        result = calculate_payroll(3_000_000, settings=TEST_SETTINGS)
        assert result.base_salary == 3_000_000
        assert result.taxable_income == 3_000_000
        assert result.nontaxable_income == 0
        assert result.national_pension.employee == result.national_pension.employer
        assert result.industrial_accident.employee == 0

    def test_zero_salary(self):
        result = calculate_payroll(0, settings=TEST_SETTINGS)
        expected_np = round(370_000 * 0.045 / 10) * 10
        assert result.national_pension.employee == expected_np
        assert result.total_employee == expected_np

    def test_negative_salary(self):
        import pytest
        with pytest.raises(ValueError):
            calculate_payroll(-100, settings=TEST_SETTINGS)

    def test_np_floor(self):
        result = calculate_payroll(200_000, settings=TEST_SETTINGS)
        expected = round(370_000 * 0.045 / 10) * 10
        assert result.national_pension.employee == expected

    def test_np_cap(self):
        result = calculate_payroll(10_000_000, settings=TEST_SETTINGS)
        expected = round(5_900_000 * 0.045 / 10) * 10
        assert result.national_pension.employee == expected

    def test_employer_total(self):
        result = calculate_payroll(3_000_000, settings=TEST_SETTINGS)
        total = (
            result.national_pension.employer
            + result.health_insurance.employer
            + result.long_term_care.employer
            + result.employment_insurance.employer
            + result.industrial_accident.employer
            + result.retirement_provision
        )
        assert result.total_employer == total

    def test_employee_total(self):
        result = calculate_payroll(3_000_000, settings=TEST_SETTINGS)
        total = (
            result.national_pension.employee
            + result.health_insurance.employee
            + result.long_term_care.employee
            + result.employment_insurance.employee
        )
        assert result.total_employee == total

    # ── 수당 비과세 테스트 ──────────────────────────────
    def test_meal_within_limit(self):
        result = calculate_payroll(3_000_000, meal=200_000, settings=TEST_SETTINGS)
        assert result.allowances.meal_nontaxable == 200_000
        assert result.allowances.meal_taxable == 0
        assert result.taxable_income == 3_000_000

    def test_meal_over_limit(self):
        result = calculate_payroll(3_000_000, meal=300_000, settings=TEST_SETTINGS)
        assert result.allowances.meal_nontaxable == 200_000
        assert result.allowances.meal_taxable == 100_000
        assert result.taxable_income == 3_100_000

    def test_fuel_over_limit(self):
        result = calculate_payroll(3_000_000, fuel=250_000, settings=TEST_SETTINGS)
        assert result.allowances.fuel_nontaxable == 200_000
        assert result.allowances.fuel_taxable == 50_000

    def test_childcare_within_limit(self):
        result = calculate_payroll(3_000_000, childcare=100_000, settings=TEST_SETTINGS)
        assert result.allowances.childcare_nontaxable == 100_000
        assert result.allowances.childcare_taxable == 0
        assert result.nontaxable_income == 100_000

    def test_childcare_over_limit(self):
        result = calculate_payroll(3_000_000, childcare=150_000, settings=TEST_SETTINGS)
        assert result.allowances.childcare_nontaxable == 100_000
        assert result.allowances.childcare_taxable == 50_000
        assert result.taxable_income == 3_050_000

    # ── 과세 수당 테스트 ────────────────────────────────
    def test_taxable_allowances(self):
        result = calculate_payroll(
            3_000_000,
            overtime=200_000,
            holiday_work=150_000,
            position=100_000,
            settings=TEST_SETTINGS,
        )
        assert result.taxable_income == 3_450_000
        assert result.allowances.overtime == 200_000

    def test_all_allowances(self):
        result = calculate_payroll(
            3_000_000,
            weekly_holiday=200_000,
            monthly_leave=100_000,
            overtime=50_000,
            meal=200_000,
            fuel=200_000,
            childcare=100_000,
            other_nontaxable=50_000,
            settings=TEST_SETTINGS,
        )
        assert result.taxable_income == 3_350_000
        assert result.nontaxable_income == 550_000
        assert result.total_pay == 3_900_000
        assert result.net_pay == result.total_pay - result.total_deduction


class TestAPI:
    """API 엔드포인트 테스트"""

    def test_calculate_basic(self):
        response = client.post("/api/payroll/calculate", json={"base_salary": 3_000_000})
        assert response.status_code == 200
        data = response.json()
        assert data["base_salary"] == 3_000_000
        assert data["taxable_income"] == 3_000_000
        assert "net_pay" in data

    def test_calculate_with_allowances(self):
        response = client.post("/api/payroll/calculate", json={
            "base_salary": 3_000_000,
            "allowances": {
                "weekly_holiday": 200_000,
                "overtime": 100_000,
                "meal": 200_000,
                "fuel": 300_000,
                "childcare": 150_000,
            }
        })
        assert response.status_code == 200
        data = response.json()
        a = data["allowances"]
        assert a["meal_nontaxable"] == 200_000
        assert a["fuel_nontaxable"] == 200_000
        assert a["fuel_taxable"] == 100_000
        assert a["childcare_nontaxable"] == 100_000
        assert a["childcare_taxable"] == 50_000
        # 과세: 300만 + 주휴20만 + 연장10만 + 유류과세10만 + 육아과세5만 = 345만
        assert data["taxable_income"] == 3_450_000
        # 비과세: 식대20만 + 유류비과세20만 + 육아비과세10만 = 50만
        assert data["nontaxable_income"] == 500_000

    def test_invalid_salary(self):
        response = client.post("/api/payroll/calculate", json={"base_salary": -1000})
        assert response.status_code == 422

    def test_missing_field(self):
        response = client.post("/api/payroll/calculate", json={})
        assert response.status_code == 422

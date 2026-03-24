import pytest
from fastapi.testclient import TestClient

from app.services import settings_store


@pytest.fixture(autouse=True)
def temp_settings_file(tmp_path):
    """테스트마다 임시 설정 파일을 사용한다."""
    test_file = tmp_path / "settings.json"
    original = settings_store.DATA_FILE
    settings_store.DATA_FILE = test_file
    yield test_file
    settings_store.DATA_FILE = original


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


class TestSettingsStore:
    def test_seed_defaults(self):
        settings_store.seed_defaults_if_empty()
        s = settings_store.load_settings()
        assert s["national_pension_rate"] == 0.045
        assert s["minimum_wage"] == 10030
        assert s["apply_year"] == 2025

    def test_update_settings(self):
        settings_store.seed_defaults_if_empty()
        updated = settings_store.update_settings({"minimum_wage": 11000})
        assert updated["minimum_wage"] == 11000
        # 다른 값은 유지
        assert updated["national_pension_rate"] == 0.045

    def test_reset_settings(self):
        settings_store.seed_defaults_if_empty()
        settings_store.update_settings({"minimum_wage": 99999})
        reset = settings_store.reset_settings()
        assert reset["minimum_wage"] == 10030


class TestSettingsAPI:
    def test_get_settings(self, client):
        settings_store.seed_defaults_if_empty()
        res = client.get("/api/settings/")
        assert res.status_code == 200
        data = res.json()
        assert data["minimum_wage"] == 10030
        assert data["apply_year"] == 2025

    def test_update_settings(self, client):
        settings_store.seed_defaults_if_empty()
        res = client.put("/api/settings/", json={
            "minimum_wage": 11000,
            "apply_year": 2026,
            "national_pension_rate": 0.045,
            "national_pension_floor": 390000,
            "national_pension_cap": 6170000,
            "health_insurance_rate": 0.03545,
            "long_term_care_rate": 0.1281,
            "employment_insurance_employee": 0.009,
            "employment_insurance_employer": 0.009,
            "industrial_accident_rate": 0.007,
            "meal_nontax_limit": 200000,
            "fuel_nontax_limit": 200000,
            "childcare_nontax_limit": 100000,
        })
        assert res.status_code == 200
        data = res.json()
        assert data["minimum_wage"] == 11000
        assert data["apply_year"] == 2026

    def test_reset_settings(self, client):
        settings_store.seed_defaults_if_empty()
        # 변경 후 초기화
        client.put("/api/settings/", json={
            "minimum_wage": 99999,
            "apply_year": 2030,
            "national_pension_rate": 0.05,
            "national_pension_floor": 400000,
            "national_pension_cap": 7000000,
            "health_insurance_rate": 0.04,
            "long_term_care_rate": 0.15,
            "employment_insurance_employee": 0.01,
            "employment_insurance_employer": 0.01,
            "industrial_accident_rate": 0.01,
            "meal_nontax_limit": 300000,
            "fuel_nontax_limit": 300000,
            "childcare_nontax_limit": 200000,
        })
        res = client.post("/api/settings/reset")
        assert res.status_code == 200
        assert res.json()["minimum_wage"] == 10030

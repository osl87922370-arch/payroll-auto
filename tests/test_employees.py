import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.services import employee_store

# 테스트용 임시 파일 사용
@pytest.fixture(autouse=True)
def temp_data_file(tmp_path):
    """테스트마다 임시 JSON 파일을 사용한다."""
    test_file = tmp_path / "employees.json"
    original = employee_store.DATA_FILE
    employee_store.DATA_FILE = test_file
    yield test_file
    employee_store.DATA_FILE = original


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


class TestEmployeeStore:
    """employee_store 단위 테스트"""

    def test_seed_defaults(self):
        employee_store.seed_defaults_if_empty()
        employees = employee_store.load_employees()
        assert len(employees) == 6
        ids = [e["id"] for e in employees]
        assert "emp_1" in ids
        assert "emp_6" in ids

    def test_get_employee(self):
        employee_store.seed_defaults_if_empty()
        emp = employee_store.get_employee("emp_1")
        assert emp is not None
        assert emp["name"] == ""
        assert emp["role"] == ""

    def test_get_nonexistent(self):
        employee_store.seed_defaults_if_empty()
        emp = employee_store.get_employee("nobody")
        assert emp is None

    def test_update_employee(self):
        employee_store.seed_defaults_if_empty()
        updated = employee_store.update_employee("emp_1", {
            "name": "홍길동",
            "role": "주방장",
            "base_salary": 3_500_000,
            "allowances": {"meal": 200_000},
        })
        assert updated["base_salary"] == 3_500_000
        assert updated["name"] == "홍길동"
        assert updated["role"] == "주방장"
        emp = employee_store.get_employee("emp_1")
        assert emp["base_salary"] == 3_500_000
        assert emp["allowances"]["meal"] == 200_000


class TestEmployeeAPI:
    """직원 API 엔드포인트 테스트"""

    def test_list_employees(self, client):
        employee_store.seed_defaults_if_empty()
        res = client.get("/api/employees/")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 6

    def test_get_employee(self, client):
        employee_store.seed_defaults_if_empty()
        res = client.get("/api/employees/emp_2")
        assert res.status_code == 200
        assert res.json()["role"] == ""

    def test_get_nonexistent(self, client):
        employee_store.seed_defaults_if_empty()
        res = client.get("/api/employees/nobody")
        assert res.status_code == 404

    def test_update_employee(self, client):
        employee_store.seed_defaults_if_empty()
        res = client.put("/api/employees/emp_1", json={
            "base_salary": 3_500_000,
            "allowances": {"weekly_holiday": 100_000, "meal": 200_000},
        })
        assert res.status_code == 200
        data = res.json()
        assert data["base_salary"] == 3_500_000

    def test_get_statement(self, client):
        employee_store.seed_defaults_if_empty()
        # 먼저 급여 설정
        client.put("/api/employees/emp_1", json={
            "base_salary": 3_000_000,
            "allowances": {"meal": 200_000},
        })
        res = client.get("/api/employees/emp_1/statement")
        assert res.status_code == 200
        data = res.json()
        assert data["employee_id"] == "emp_1"
        assert data["base_salary"] == 3_000_000
        assert data["net_pay"] > 0

    def test_statement_no_salary(self, client):
        employee_store.seed_defaults_if_empty()
        res = client.get("/api/employees/emp_1/statement")
        assert res.status_code == 400

    def test_calculate_all(self, client):
        employee_store.seed_defaults_if_empty()
        # 2명 급여 설정
        client.put("/api/employees/emp_1", json={"base_salary": 3_500_000})
        client.put("/api/employees/emp_2", json={"base_salary": 2_800_000})

        res = client.post("/api/employees/calculate-all")
        assert res.status_code == 200
        data = res.json()
        assert len(data["results"]) == 2
        assert data["total_pay_sum"] == 3_500_000 + 2_800_000
        assert data["total_net_pay_sum"] > 0

    def test_calculate_all_empty(self, client):
        employee_store.seed_defaults_if_empty()
        res = client.post("/api/employees/calculate-all")
        assert res.status_code == 200
        assert len(res.json()["results"]) == 0

    def test_create_employee(self, client):
        employee_store.seed_defaults_if_empty()
        res = client.post("/api/employees/", json={"name": "김철수", "role": "주방장"})
        assert res.status_code == 200
        data = res.json()
        assert data["name"] == "김철수"
        assert data["role"] == "주방장"
        assert data["id"].startswith("emp_")
        # 목록에 7명
        res2 = client.get("/api/employees/")
        assert len(res2.json()) == 7

    def test_delete_employee(self, client):
        employee_store.seed_defaults_if_empty()
        # 삭제
        res = client.delete("/api/employees/emp_6")
        assert res.status_code == 200
        # 목록에 5명
        res2 = client.get("/api/employees/")
        assert len(res2.json()) == 5

    def test_delete_nonexistent(self, client):
        employee_store.seed_defaults_if_empty()
        res = client.delete("/api/employees/nobody")
        assert res.status_code == 404

    def test_create_then_delete(self, client):
        employee_store.seed_defaults_if_empty()
        # 추가
        res = client.post("/api/employees/", json={"name": "신입", "role": "홀직원"})
        new_id = res.json()["id"]
        res2 = client.get("/api/employees/")
        assert len(res2.json()) == 7
        # 삭제
        res3 = client.delete(f"/api/employees/{new_id}")
        assert res3.status_code == 200
        res4 = client.get("/api/employees/")
        assert len(res4.json()) == 6

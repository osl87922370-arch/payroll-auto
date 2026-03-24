"""직원 데이터 JSON 파일 저장소."""

import json
import uuid
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "employees.json"

DEFAULT_EMPLOYEES = [
    {"id": "emp_1", "name": "", "role": "", "base_salary": 0, "allowances": {}},
    {"id": "emp_2", "name": "", "role": "", "base_salary": 0, "allowances": {}},
    {"id": "emp_3", "name": "", "role": "", "base_salary": 0, "allowances": {}},
    {"id": "emp_4", "name": "", "role": "", "base_salary": 0, "allowances": {}},
    {"id": "emp_5", "name": "", "role": "", "base_salary": 0, "allowances": {}},
    {"id": "emp_6", "name": "", "role": "", "base_salary": 0, "allowances": {}},
]


def seed_defaults_if_empty() -> None:
    """데이터 파일이 없으면 기본 직원 데이터를 생성한다."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        save_employees(DEFAULT_EMPLOYEES)


def load_employees() -> list[dict]:
    """전체 직원 목록을 반환한다."""
    if not DATA_FILE.exists():
        seed_defaults_if_empty()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_employees(employees: list[dict]) -> None:
    """직원 목록을 JSON 파일에 저장한다."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(employees, f, ensure_ascii=False, indent=2)


def get_employee(employee_id: str) -> dict | None:
    """특정 직원 데이터를 반환한다."""
    employees = load_employees()
    for emp in employees:
        if emp["id"] == employee_id:
            return emp
    return None


def update_employee(employee_id: str, data: dict) -> dict | None:
    """직원의 급여/수당 정보를 업데이트한다."""
    employees = load_employees()
    for emp in employees:
        if emp["id"] == employee_id:
            if data.get("name") is not None:
                emp["name"] = data["name"]
            if data.get("role") is not None:
                emp["role"] = data["role"]
            emp["base_salary"] = data["base_salary"]
            emp["dependents"] = data.get("dependents", 1)
            emp["allowances"] = data.get("allowances", {})
            save_employees(employees)
            return emp
    return None


def add_employee(name: str = "", role: str = "") -> dict:
    """새 직원을 추가한다. ID는 자동 생성."""
    employees = load_employees()
    new_id = "emp_" + uuid.uuid4().hex[:8]
    new_emp = {"id": new_id, "name": name, "role": role, "base_salary": 0, "allowances": {}}
    employees.append(new_emp)
    save_employees(employees)
    return new_emp


def delete_employee(employee_id: str) -> bool:
    """직원을 삭제한다."""
    employees = load_employees()
    new_list = [e for e in employees if e["id"] != employee_id]
    if len(new_list) == len(employees):
        return False
    save_employees(new_list)
    return True

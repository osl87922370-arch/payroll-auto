from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import payroll, employees, settings
from app.services.employee_store import seed_defaults_if_empty
from app.services.settings_store import seed_defaults_if_empty as seed_settings

app = FastAPI(title="급여 자동정산 서비스", version="0.3.0")

app.include_router(payroll.router, prefix="/api/payroll", tags=["payroll"])
app.include_router(employees.router, prefix="/api/employees", tags=["employees"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])

# 정적 파일 서빙
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 기본 데이터 생성
seed_defaults_if_empty()
seed_settings()


@app.get("/")
def root():
    return FileResponse(static_dir / "index.html")


@app.get("/employees")
def employees_page():
    return FileResponse(static_dir / "employees.html")


@app.get("/settings")
def settings_page():
    return FileResponse(static_dir / "settings.html")


@app.get("/statement/{employee_id}")
def statement_page(employee_id: str):
    return FileResponse(static_dir / "statement.html")

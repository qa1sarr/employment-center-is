import os

DB_SERVER = os.environ.get("DB_SERVER", r"BORIBEK-QAISAR\BORIBEK")
DB_NAME = os.environ.get("DB_NAME", "EmploymentCenter")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
LAB11_DEMO = os.environ.get("LAB11_DEMO", "") == "1"


def connection_string() -> str:
    return (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={DB_SERVER};DATABASE={DB_NAME};"
        "Trusted_Connection=yes;TrustServerCertificate=yes;"
    )

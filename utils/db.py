import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def get_engine():
    """Create and return SQLAlchemy engine."""
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    database = os.getenv("DB_DATABASE", "bi_support_telkom_ridar")
    username = os.getenv("DB_USERNAME", "root")
    password = os.getenv("DB_PASSWORD", "")

    url = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4"
    engine = create_engine(url, pool_pre_ping=True, pool_recycle=3600)
    return engine

@st.cache_resource
def get_cached_engine():
    """Cached engine for Streamlit."""
    return get_engine()

def run_query(query: str, params: dict = None):
    """Execute a query and return results as a list of dicts."""
    engine = get_cached_engine()
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        columns = result.keys()
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]

def execute_ddl(sql: str):
    """Execute DDL (CREATE/DROP/ALTER) statements."""
    engine = get_engine()
    with engine.connect() as conn:
        for statement in sql.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()

def init_database():
    """Initialize database schema if tables don't exist."""
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'warehouse', 'schema.sql')
    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        execute_ddl(sql)
    
    # Pastikan kolom etl_logs lengkap (handle tabel lama)
    _migrate_etl_logs()

def _migrate_etl_logs():
    """Tambah kolom etl_logs yang mungkin belum ada."""
    engine = get_engine()
    columns_to_add = {
        "etl_name":         "VARCHAR(255) NOT NULL DEFAULT ''",
        "source_file":      "VARCHAR(255) DEFAULT NULL",
        "total_records":    "INT DEFAULT 0",
        "inserted_records": "INT DEFAULT 0",
        "skipped_records":  "INT DEFAULT 0",
        "failed_records":   "INT DEFAULT 0",
        "error_message":    "TEXT DEFAULT NULL",
        "finished_at":      "DATETIME DEFAULT NULL",
        "duration_seconds": "INT DEFAULT NULL",
    }
    with engine.connect() as conn:
        for col, definition in columns_to_add.items():
            try:
                conn.execute(text(f"ALTER TABLE etl_logs ADD COLUMN {col} {definition}"))
                conn.commit()
            except Exception:
                pass  # Kolom sudah ada, skip

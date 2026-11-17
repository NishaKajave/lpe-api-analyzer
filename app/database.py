from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import DATABASE_URL

class Base(DeclarativeBase): pass

kwargs = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def ensure_schema_migrations(eng):
    """Automatically ensure new OpsZero and Live Data columns exist in SQLite."""
    try:
        with eng.connect() as conn:
            # Check analyses table
            res = conn.execute(text("PRAGMA table_info(analyses);")).fetchall()
            existing_cols = {row[1] for row in res}
            new_cols = [
                ("is_live", "BOOLEAN DEFAULT 0"),
                ("live_url", "VARCHAR(500)"),
                ("latency_ms", "FLOAT DEFAULT 0.0"),
                ("code_patch", "TEXT"),
                ("opszero_level", "VARCHAR(30) DEFAULT 'L2-Assisted'"),
                ("mttr_saved_minutes", "INTEGER DEFAULT 35"),
            ]
            for col_name, col_type in new_cols:
                if existing_cols and col_name not in existing_cols:
                    try:
                        conn.execute(text(f"ALTER TABLE analyses ADD COLUMN {col_name} {col_type};"))
                        conn.commit()
                    except Exception:
                        pass

            # Check attempts table
            res_att = conn.execute(text("PRAGMA table_info(attempts);")).fetchall()
            existing_att_cols = {row[1] for row in res_att}
            if existing_att_cols and "code_patch" not in existing_att_cols:
                try:
                    conn.execute(text("ALTER TABLE attempts ADD COLUMN code_patch TEXT;"))
                    conn.commit()
                except Exception:
                    pass
    except Exception:
        pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

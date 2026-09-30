import os
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "meeting_minutes_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin1234")


DATABASE_CONN_INFO = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

_pool = None
_checkpointer = None


def get_memory():
    """
    Return the persistent PostgresSaver checkpointer.
    """
    global _pool, _checkpointer
    if _checkpointer is None:
        _pool = ConnectionPool(
            conninfo=DATABASE_CONN_INFO,
            max_size=5,
            kwargs={"autocommit": True, "row_factory": dict_row}
        )
        _checkpointer = PostgresSaver(_pool)  # type: ignore[arg-type]
        _checkpointer.setup()
    return _checkpointer

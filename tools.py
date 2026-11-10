import sqlite3
from pydantic import BaseModel

DB_PATH = "data/shop.db"

def _connect():
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

class RunSQLArgs(BaseModel):
    query: str

def get_schema() -> str:
    conn = _connect()
    out = []
    for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        cols = conn.execute(f"PRAGMA table_info({name})").fetchall()
        out.append(f"{name}: " + ", ".join(f"{c[1]} {c[2]}" for c in cols))
    conn.close()
    return "\n".join(out)

def run_sql(args: RunSQLArgs, limit: int = 50) -> str:
    conn = _connect()
    try:
        cur = conn.execute(args.query)
        rows = cur.fetchmany(limit)
        header = [d[0] for d in cur.description]
        return str(header) + "\n" + "\n".join(map(str, rows)) if rows else "0 rows"
    except Exception as e:
        return f"ERROR: {e}"
    finally:
        conn.close()

if __name__ == "__main__":
    print(get_schema())
    print(run_sql(RunSQLArgs(query="SELECT category, SUM(total_price) FROM orders o JOIN products p USING(product_id) GROUP BY category")))
    print(run_sql(RunSQLArgs(query="SELECT * FROM yoxdur")))   
    print(run_sql(RunSQLArgs(query="DELETE FROM orders")))     

from tools import RunSQLArgs

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_schema",
            "description": "Return all table names and their columns. Call this first if you do not know the exact table or column names.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_sql",
            "description": "Run a read-only SQLite SELECT query and return up to 50 rows. If it returns an ERROR, read the message and fix the query.",
            "parameters": RunSQLArgs.model_json_schema(),
        },
    },
]
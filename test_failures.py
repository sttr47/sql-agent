from agent import execute_tool

cases = {
    "pis SQL (olmayan sütun)": ("run_sql", '{"query": "SELECT revenue FROM orders"}'),
    "yanlış JSON":              ("run_sql", '{query: SELECT 1'),
    "yanlış arqument tipi":     ("run_sql", '{"query": 123}'),
    "çatışmayan arqument":      ("run_sql", '{}'),
    "olmayan tool":             ("send_email", '{"to": "a@b.com"}'),
    "yazma cəhdi":              ("run_sql", '{"query": "DELETE FROM orders"}'),
    "boş nəticə":               ("run_sql", '{"query": "SELECT * FROM orders WHERE order_date LIKE \'2030%\'"}'),
}

for name, (tool, args) in cases.items():
    print(f"--- {name}\n{execute_tool(tool, args)}\n")
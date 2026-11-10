import os, json
from dotenv import load_dotenv
from openai import OpenAI
from schemas import TOOL_SCHEMAS
from tools import get_schema, run_sql, RunSQLArgs

load_dotenv()
client = OpenAI(api_key=os.getenv("API_KEY"),
                base_url="https://api.groq.com/openai/v1")
MODEL = "openai/gpt-oss-120b"

messages = [{"role": "user", "content": "Hansı kateqoriyanın ümumi gəliri ən yüksəkdir?"}]

response = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOL_SCHEMAS)
msg = response.choices[0].message

print("Mətn cavabı:", msg.content)
print("Tool call-lar:", msg.tool_calls)

if msg.tool_calls:
    call = msg.tool_calls[0]
    args = json.loads(call.function.arguments)
    print(f"\nLLM bunu seçdi: {call.function.name}({args})")
    if call.function.name == "get_schema":
        print(get_schema())
    elif call.function.name == "run_sql":
        print(run_sql(RunSQLArgs(**args)))
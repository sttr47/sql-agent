import os, json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError
from schemas import TOOL_SCHEMAS
from tools import get_schema, run_sql, RunSQLArgs

load_dotenv()
client = OpenAI(api_key=os.getenv("API_KEY"),
                base_url="https://api.groq.com/openai/v1")
MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = (
    "You are a data analyst assistant for a sales database. "
    "Your only tools are get_schema and run_sql (read-only SELECT queries). "
    "You cannot modify data, send emails, or predict the future. "
    "Answer only using data you retrieve with your tools and never invent numbers. "
    "If the user mentions a column or table that does not exist, say so explicitly "
    "before using the closest alternative. "
    "If a request is impossible with your tools, explain briefly why. "
    "Always reply in the same language as the user's question. "
    "Double-check years, names, and numbers in your final answer against the tool results."
)

def execute_tool(name, raw_args):
    """Tool-u icra edir. Xəta atmır, xətanı mətn kimi qaytarır ki, LLM düzəldə bilsin."""
    try:
        args = json.loads(raw_args or "{}")
        if name == "get_schema":
            return get_schema()
        if name == "run_sql":
            return run_sql(RunSQLArgs(**args))
        return f"ERROR: unknown tool '{name}'"
    except json.JSONDecodeError:
        return "ERROR: arguments are not valid JSON"
    except ValidationError as e:
        return f"ERROR: invalid arguments: {e}"

def run_agent(question, max_steps=8):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    trace = []

    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SCHEMAS)
        msg = response.choices[0].message

        if not msg.tool_calls:
            trace.append({"step": step, "final_answer": msg.content})
            print(f"\n[Step {step}] FINAL ANSWER:\n{msg.content}")
            return msg.content, trace

        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name,
                              "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ],
        })

        for tc in msg.tool_calls:
            result = execute_tool(tc.function.name, tc.function.arguments)
            print(f"\n[Step {step}] TOOL: {tc.function.name}")
            print(f"  args:   {tc.function.arguments}")
            print(f"  result: {result[:300]}")
            trace.append({"step": step, "tool": tc.function.name,
                          "arguments": tc.function.arguments, "result": result})
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    note = "Step limitinə çatdım, cavab tapa bilmədim."
    trace.append({"step": max_steps, "final_answer": note})
    return note, trace

if __name__ == "__main__":
    import sys
    question = " ".join(sys.argv[1:]) or "Hansı kateqoriyanın ümumi gəliri ən yüksəkdir?"
    answer, trace = run_agent(question)
    os.makedirs("traces", exist_ok=True)
    with open(f"traces/{abs(hash(question))}.json", "w", encoding="utf-8") as f:
        json.dump({"question": question, "trace": trace}, f, ensure_ascii=False, indent=2)
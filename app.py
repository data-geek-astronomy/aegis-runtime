from __future__ import annotations

import json
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from runtime import AssistantRuntime


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
runtime = AssistantRuntime(DATA_DIR / "aegis.db")
app = FastAPI(title="Aegis Runtime")


EXAMPLES = [
    "What did I discuss with Priya about the launch?",
    "Summarize what is on my screen",
    "Open the Aegis runtime spec document",
    "Remind me to reply to Alex after my meeting",
    "Summarize my runtime architecture notes from yesterday",
]


class AskRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    options = "".join(f"<option value=\"{prompt}\">{prompt}</option>" for prompt in EXAMPLES)
    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Aegis Runtime</title>
        <style>
          :root {{ color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
          body {{ margin: 0; background: #f5f7fa; color: #17202a; }}
          main {{ max-width: 1120px; margin: 0 auto; padding: 40px 20px; }}
          h1 {{ margin: 0 0 8px; font-size: 36px; }}
          p {{ margin: 0 0 24px; color: #526070; line-height: 1.5; }}
          .panel {{ background: white; border: 1px solid #dce3ea; border-radius: 8px; padding: 18px; margin-bottom: 16px; box-shadow: 0 8px 24px rgba(23, 32, 42, 0.06); }}
          label {{ display: block; font-weight: 650; margin-bottom: 8px; }}
          textarea, select, pre {{ box-sizing: border-box; width: 100%; border: 1px solid #cbd5df; border-radius: 6px; font: inherit; }}
          textarea {{ min-height: 88px; padding: 12px; resize: vertical; }}
          select {{ padding: 10px; margin-bottom: 10px; background: white; }}
          button {{ margin-top: 12px; border: 0; border-radius: 6px; background: #1663c7; color: white; padding: 11px 16px; font-weight: 700; cursor: pointer; }}
          button:disabled {{ opacity: 0.6; cursor: wait; }}
          .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
          pre {{ min-height: 180px; margin: 0; padding: 12px; overflow: auto; background: #101820; color: #edf6ff; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px; }}
          @media (max-width: 760px) {{ .grid {{ grid-template-columns: 1fr; }} h1 {{ font-size: 30px; }} }}
        </style>
      </head>
      <body>
        <main>
          <h1>Aegis Runtime</h1>
          <p>Local-first assistant runtime demo with personal context retrieval, screen awareness, permission checks, audit logging, and latency profiling.</p>
          <section class="panel">
            <label for="examples">Demo prompt</label>
            <select id="examples">{options}</select>
            <label for="message">Assistant request</label>
            <textarea id="message">{EXAMPLES[0]}</textarea>
            <button id="run">Run request</button>
          </section>
          <section class="grid">
            <div class="panel">
              <label>Assistant response</label>
              <pre id="answer">Ready.</pre>
            </div>
            <div class="panel">
              <label>Runtime trace</label>
              <pre id="trace">{{}}</pre>
            </div>
          </section>
        </main>
        <script>
          const examples = document.getElementById("examples");
          const message = document.getElementById("message");
          const run = document.getElementById("run");
          const answer = document.getElementById("answer");
          const trace = document.getElementById("trace");
          examples.addEventListener("change", () => {{ message.value = examples.value; }});
          run.addEventListener("click", async () => {{
            run.disabled = true;
            answer.textContent = "Running...";
            try {{
              const res = await fetch("/api/ask", {{
                method: "POST",
                headers: {{ "Content-Type": "application/json" }},
                body: JSON.stringify({{ message: message.value }})
              }});
              const data = await res.json();
              answer.textContent = data.answer;
              trace.textContent = JSON.stringify({{
                request_id: data.request_id,
                intent: data.intent,
                tool: data.tool,
                timings_ms: data.timings_ms,
                audit: data.audit
              }}, null, 2);
            }} catch (err) {{
              answer.textContent = String(err);
            }} finally {{
              run.disabled = false;
            }}
          }});
        </script>
      </body>
    </html>
    """


@app.post("/api/ask")
def ask(request: AskRequest) -> dict:
    return runtime.handle(request.message)


@app.get("/health")
def health() -> dict:
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)

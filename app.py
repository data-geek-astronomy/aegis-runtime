from __future__ import annotations

import json
from pathlib import Path

import gradio as gr

from runtime import AssistantRuntime


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
runtime = AssistantRuntime(DATA_DIR / "aegis.db")


EXAMPLES = [
    "What did I discuss with Priya about the launch?",
    "Summarize what is on my screen",
    "Open the Aegis runtime spec document",
    "Remind me to reply to Alex after my meeting",
    "Summarize my runtime architecture notes from yesterday",
]


def ask(message: str, history: list[dict] | None = None):
    response = runtime.handle(message)
    audit_rows = [
        [event["created_at"], event["tool"], event["permission"], event["decision"]]
        for event in response["audit"]
    ]
    profile = json.dumps(response["timings_ms"], indent=2)
    trace = json.dumps(
        {
            "request_id": response["request_id"],
            "intent": response["intent"],
            "tool": response["tool"],
            "matches": response["data"].get("matches", []),
        },
        indent=2,
    )
    return response["answer"], audit_rows, profile, trace


with gr.Blocks(title="Aegis Runtime") as demo:
    gr.Markdown(
        """
        # Aegis Runtime
        Privacy-preserving on-device assistant runtime demo with personal context retrieval, tool routing,
        permission checks, audit logging, and latency profiling.
        """
    )
    with gr.Row():
        query = gr.Textbox(label="Assistant request", value=EXAMPLES[0], lines=2)
        run = gr.Button("Run", variant="primary")
    gr.Examples(EXAMPLES, inputs=query)
    answer = gr.Textbox(label="Assistant response", lines=8)
    with gr.Row():
        profile = gr.Code(label="Latency profile", language="json")
        trace = gr.Code(label="Runtime trace", language="json")
    audit = gr.Dataframe(
        headers=["Time", "Tool", "Permission", "Decision"],
        label="Privacy audit log",
        interactive=False,
    )
    run.click(ask, inputs=query, outputs=[answer, audit, profile, trace])
    query.submit(ask, inputs=query, outputs=[answer, audit, profile, trace])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

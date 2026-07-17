from __future__ import annotations

from statistics import mean

from runtime import AssistantRuntime


PROMPTS = [
    "What did I discuss with Priya about the launch?",
    "Summarize what is on my screen",
    "Open the Aegis Runtime Spec document",
    "Remind me to reply to Alex after my meeting",
    "Summarize my runtime architecture notes from yesterday",
]


def main() -> None:
    runtime = AssistantRuntime(seed=True)
    totals: list[float] = []
    for prompt in PROMPTS:
        response = runtime.handle(prompt)
        total = response["timings_ms"]["total"]
        totals.append(total)
        print(f"{total:7.2f} ms | {response['intent']:18} | {prompt}")
    print(f"\nAverage: {mean(totals):.2f} ms across {len(PROMPTS)} requests")


if __name__ == "__main__":
    main()

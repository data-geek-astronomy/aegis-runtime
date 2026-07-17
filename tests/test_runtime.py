from runtime import AssistantRuntime


def test_context_question_finds_priya_launch():
    runtime = AssistantRuntime(seed=True)
    response = runtime.handle("What did I discuss with Priya about the launch?")
    assert response["ok"]
    assert response["intent"] == "context_question"
    assert "Priya" in response["answer"]
    assert "launch" in response["answer"].lower()
    assert response["timings_ms"]["total"] >= 0


def test_screen_awareness_uses_permissioned_tool():
    runtime = AssistantRuntime(seed=True)
    response = runtime.handle("Summarize what is on my screen")
    assert response["tool"] == "summarize_screen"
    assert "current screen" in response["answer"].lower()
    assert response["audit"][0]["permission"] == "screen.read"


def test_reminder_creation_is_audited():
    runtime = AssistantRuntime(seed=True)
    response = runtime.handle("Remind me to reply to Alex after my meeting")
    assert response["tool"] == "create_reminder"
    assert "Created reminder" in response["answer"]
    assert response["audit"][0]["permission"] == "reminders.write"


def test_document_opening():
    runtime = AssistantRuntime(seed=True)
    response = runtime.handle("Open the Aegis Runtime Spec document")
    assert response["tool"] == "open_document"
    assert "Aegis Runtime Spec" in response["answer"]

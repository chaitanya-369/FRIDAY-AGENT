from unittest.mock import Mock, patch

from friday.core.brain import FridayBrain


@patch("friday.core.brain.groq.Groq")
@patch("friday.core.brain.genai.configure")
@patch("friday.core.brain.anthropic.Anthropic")
def test_sliding_window_memory(mock_anthropic, mock_genai, mock_groq):
    brain = FridayBrain()

    # Fill memory with 45 turns (90 messages)
    for i in range(45):
        brain._update_history("user", f"Message {i}")
        brain._update_history("assistant", f"Reply {i}")

    # Should keep only the last 40 messages (20 turns)
    assert len(brain.conversation_history) == 40

    assert brain.conversation_history[0]["content"] == "Message 25"
    assert brain.conversation_history[-1]["content"] == "Reply 44"


@patch("friday.core.brain.groq.Groq")
@patch("friday.core.brain.genai.configure")
@patch("friday.core.brain.anthropic.Anthropic")
@patch("friday.core.brain.datetime")
def test_system_prompt_formatting(mock_datetime, mock_anthropic, mock_genai, mock_groq):
    # Mock datetime to return a specific timestamp and day
    mock_now = Mock()
    mock_now.isoformat.return_value = "2026-04-22T10:00:00"
    mock_now.strftime.return_value = "Wednesday"
    mock_datetime.now.return_value = mock_now

    brain = FridayBrain()
    system_prompt = brain._get_system_prompt()

    assert "2026-04-22T10:00:00" in system_prompt
    assert "Wednesday" in system_prompt
    assert "You address the user exclusively as 'Boss'" in system_prompt

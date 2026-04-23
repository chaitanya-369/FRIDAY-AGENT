"""
tests/test_session.py

Unit tests for friday/llm/session.py — ActiveModelSession singleton.

Tests:
  - Default initialization from settings
  - set() writes to DB and updates in-memory cache
  - Switch history is populated and capped at 10
  - reset_to_default() reverts to settings values
  - notify_hard_failure() auto-switches for system sessions
  - notify_hard_failure() does NOT auto-switch for user-set sessions
  - Thread safety: concurrent set() calls don't corrupt state
"""

import threading
import time

import pytest
from sqlmodel import Session, select

from friday.core.database import engine
from friday.llm.models.db_models import ActiveSession
from friday.llm.session import ActiveModelSession


@pytest.fixture(autouse=True)
def clean_session_table():
    """Remove the active_session row before each test so state is fresh."""
    with Session(engine) as db:
        row = db.exec(select(ActiveSession).where(ActiveSession.id == 1)).first()
        if row:
            db.delete(row)
            db.commit()
    yield
    # Clean up after
    with Session(engine) as db:
        row = db.exec(select(ActiveSession).where(ActiveSession.id == 1)).first()
        if row:
            db.delete(row)
            db.commit()


@pytest.fixture()
def session_mgr():
    """Return a fresh (non-singleton) ActiveModelSession for isolation."""
    s = ActiveModelSession()
    return s


# ── Initialization tests ───────────────────────────────────────────────────────


def test_default_initialization(session_mgr):
    """First get() creates the DB row with settings defaults."""
    from friday.config.settings import settings

    provider, model = session_mgr.get()
    assert provider == settings.default_provider
    assert model == settings.default_model


def test_get_state_returns_dict(session_mgr):
    state = session_mgr.get_state()
    assert "provider_name" in state
    assert "model_id" in state
    assert "set_by" in state
    assert "switch_history" in state


# ── Switch tests ───────────────────────────────────────────────────────────────


def test_set_updates_cache_immediately(session_mgr):
    session_mgr.set("openai", "gpt-4o", set_by="user", reason="test")
    provider, model = session_mgr.get()
    assert provider == "openai"
    assert model == "gpt-4o"


def test_set_persists_to_db(session_mgr):
    session_mgr.set("anthropic", "claude-sonnet-4-5-20250514", set_by="user")
    # New instance reads from DB
    new_mgr = ActiveModelSession()
    provider, model = new_mgr.get()
    assert provider == "anthropic"
    assert model == "claude-sonnet-4-5-20250514"


def test_switch_history_populated(session_mgr):
    # Initialize
    session_mgr.get()
    session_mgr.set("openai", "gpt-4o", set_by="user")
    session_mgr.set("groq", "llama-3.3-70b-versatile", set_by="user")

    history = session_mgr.get_history()
    assert len(history) >= 2


def test_switch_history_capped_at_10(session_mgr):
    session_mgr.get()  # init
    for i in range(12):
        session_mgr.set("groq", f"model-{i}", set_by="test")

    history = session_mgr.get_history()
    assert len(history) <= 10


def test_reset_to_default(session_mgr):
    from friday.config.settings import settings

    session_mgr.set("openai", "gpt-4o", set_by="user")
    session_mgr.reset_to_default()
    provider, model = session_mgr.get()
    assert provider == settings.default_provider
    assert model == settings.default_model


# ── Hard failure notification tests ───────────────────────────────────────────


def test_notify_hard_failure_auto_switches_for_system_session(session_mgr):
    """System-set sessions should auto-switch on hard failure."""
    session_mgr.set("groq", "llama-3.3-70b-versatile", set_by="system")
    session_mgr.notify_hard_failure(
        failed_provider="groq",
        failed_model="llama-3.3-70b-versatile",
        fallback_provider="openai",
        fallback_model="gpt-4o",
        error_summary="all keys exhausted",
    )
    provider, _ = session_mgr.get()
    assert provider == "openai"


def test_notify_hard_failure_does_not_switch_for_user_session(session_mgr):
    """User-set sessions should NOT auto-switch — honour Boss's choice."""
    session_mgr.set("anthropic", "claude-sonnet-4-5-20250514", set_by="user")
    session_mgr.notify_hard_failure(
        failed_provider="anthropic",
        failed_model="claude-sonnet-4-5-20250514",
        fallback_provider="groq",
        fallback_model="llama-3.3-70b-versatile",
        error_summary="auth error",
    )
    provider, _ = session_mgr.get()
    assert provider == "anthropic"  # unchanged


# ── Thread safety test ────────────────────────────────────────────────────────


def test_concurrent_switches_are_safe(session_mgr):
    """Multiple threads switching simultaneously should not raise or corrupt."""
    errors = []

    def switch_worker(provider, model):
        try:
            for _ in range(5):
                session_mgr.set(provider, model, set_by="thread_test")
                time.sleep(0.001)
        except Exception as e:
            errors.append(str(e))

    threads = [
        threading.Thread(target=switch_worker, args=("openai", "gpt-4o")),
        threading.Thread(
            target=switch_worker, args=("groq", "llama-3.3-70b-versatile")
        ),
        threading.Thread(
            target=switch_worker, args=("anthropic", "claude-haiku-4-5-20251001")
        ),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Thread errors: {errors}"
    # State is some valid (provider, model) — not corrupted
    provider, model = session_mgr.get()
    assert isinstance(provider, str) and len(provider) > 0
    assert isinstance(model, str) and len(model) > 0

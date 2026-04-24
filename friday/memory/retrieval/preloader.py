"""
friday/memory/retrieval/preloader.py

ProactivePreloader proactively loads memory context for upcoming tasks or events
into the agent's WorkingMemory before the session even begins.
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ProactivePreloader:
    def __init__(self, memory_bus):
        self.memory_bus = memory_bus

    def run_preload_pass(self) -> None:
        """
        Scan for tasks due within the next hour.
        If found, preload their context into working memory.
        """
        if not self.memory_bus._enabled:
            return

        now = datetime.utcnow()
        horizon = now + timedelta(hours=1)

        try:
            active_tasks = self.memory_bus.episode_store.get_active_tasks()
            upcoming_tasks = [
                t for t in active_tasks if t.due_date and now <= t.due_date <= horizon
            ]

            if not upcoming_tasks:
                self.memory_bus.working.preloaded_context = None
                return

            # Assemble a query based on the upcoming tasks
            query_terms = [t.title for t in upcoming_tasks]
            query = " ".join(query_terms)

            logger.info(f"ProactivePreloader triggered for tasks: {query}")

            # Retrieve context as if the user asked about these tasks
            ctx = self.memory_bus.get_context_for(query)

            # Stash in working memory
            self.memory_bus.working.preloaded_context = ctx

        except Exception as e:
            logger.warning(f"ProactivePreloader failed: {e}")

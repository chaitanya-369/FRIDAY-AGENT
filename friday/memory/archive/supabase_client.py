"""
friday/memory/archive/supabase_client.py

Handles asynchronous syncing of episodes and memory metadata to Supabase
for cloud archiving and telemetry.
"""

import logging

from friday.config.settings import settings
from friday.memory.types import Episode

logger = logging.getLogger(__name__)


class SupabaseArchiver:
    def __init__(self):
        self.enabled = bool(settings.supabase_url and settings.supabase_key)
        self.client = None

        if self.enabled:
            try:
                from supabase import create_client, Client

                self.client: Client = create_client(
                    settings.supabase_url, settings.supabase_key
                )
                logger.info("Supabase archiving enabled.")
            except ImportError:
                logger.warning(
                    "Supabase SDK (supabase) not installed. Archiving disabled."
                )
                self.enabled = False
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase client: {e}")
                self.enabled = False

    def archive_episode(self, episode: Episode) -> None:
        """
        Push a completed episode to the Supabase `episodes` table.
        """
        if not self.enabled or not self.client:
            return

        try:
            data = {
                "id": episode.id,
                "session_id": episode.session_id,
                "started_at": episode.started_at.isoformat(),
                "ended_at": episode.ended_at.isoformat() if episode.ended_at else None,
                "summary": episode.summary,
                "mood": episode.mood,
                "topics": episode.topics,
                "turn_count": len(episode.raw_turns),
            }

            self.client.table("episodes").upsert(data).execute()
            logger.info(f"Archived episode {episode.id} to Supabase.")
        except Exception as e:
            logger.warning(f"Failed to archive episode {episode.id} to Supabase: {e}")

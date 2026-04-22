import anthropic
import groq
import google.generativeai as genai
import sentry_sdk
from langfuse import Langfuse
from infisical_python import InfisicalClient
from datetime import datetime
from typing import List, Dict, Any, Generator

from friday.config.settings import settings
from friday.core.persona import FRIDAY_SYSTEM_PROMPT
from friday.core.database import create_db_and_tables

# Initialize Secrets Manager
if hasattr(settings, "infisical_token") and settings.infisical_token:
    infisical = InfisicalClient(token=settings.infisical_token)
    # E.g., db_url = infisical.get_secret("DATABASE_URL").secret_value

# Initialize Observability Layers
if hasattr(settings, "sentry_dsn") and settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0,
    )

if hasattr(settings, "langfuse_public_key") and settings.langfuse_public_key:
    langfuse = Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
    )


class FridayBrain:
    """
    Core intelligence component of the FRIDAY Agent.

    This class handles the LLM orchestration, maintaining conversational memory
    (via a sliding window), and streaming responses back to the client. It dynamically
    selects between Anthropic, Groq, and Gemini backends based on the application settings.
    """

    def __init__(self):
        # Initialize DB Tables on start
        create_db_and_tables()

        self.provider = settings.llm_provider.lower()
        self.model = settings.llm_model

        self.conversation_history: List[Dict[str, Any]] = []

        if self.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        elif self.provider == "groq":
            self.client = groq.Groq(api_key=settings.groq_api_key)
        elif self.provider == "gemini":
            genai.configure(api_key=settings.gemini_api_key)
            self.client = genai.GenerativeModel(
                model_name=self.model, system_instruction=self._get_system_prompt()
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _get_system_prompt(self) -> str:
        """
        Retrieves and formats the FRIDAY persona prompt with dynamic context.

        Returns:
            str: The fully formatted system prompt including current timestamp.
        """
        return FRIDAY_SYSTEM_PROMPT.format(
            timestamp=datetime.now().isoformat(), day=datetime.now().strftime("%A")
        )

    def _update_history(self, role: str, content: str):
        """
        Appends a message to the conversation history, maintaining a sliding window of max 40 messages.

        Args:
            role (str): The role of the speaker (e.g., "user", "assistant").
            content (str): The content of the message.
        """
        self.conversation_history.append({"role": role, "content": content})
        if len(self.conversation_history) > 40:
            self.conversation_history = self.conversation_history[-40:]

    def stream_process(self, user_input: str) -> Generator[str, None, None]:
        """
        Processes user input and streams the LLM response token by token.

        This method routes the request to the configured LLM provider and yields
        text chunks as they are generated, appending the full response to history upon completion.

        Args:
            user_input (str): The text input from the user.

        Yields:
            str: Incremental text chunks of the generated response.
        """
        self._update_history("user", user_input)

        try:
            if self.provider == "anthropic":
                yield from self._stream_anthropic()
            elif self.provider == "groq":
                yield from self._stream_groq()
            elif self.provider == "gemini":
                yield from self._stream_gemini()
        except Exception as e:
            yield f"\n[Error: {str(e)}]"

    def _stream_anthropic(self) -> Generator[str, None, None]:
        with self.client.messages.stream(
            model=self.model,
            max_tokens=1024,
            system=self._get_system_prompt(),
            messages=self.conversation_history,
        ) as stream:
            full_response = ""
            for text in stream.text_stream:
                full_response += text
                yield text
            self._update_history("assistant", full_response)

    def _stream_groq(self) -> Generator[str, None, None]:
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        messages.extend(self.conversation_history)

        stream = self.client.chat.completions.create(
            model=self.model, messages=messages, max_tokens=1024, stream=True
        )
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                text = chunk.choices[0].delta.content
                full_response += text
                yield text
        self._update_history("assistant", full_response)

    def _stream_gemini(self) -> Generator[str, None, None]:
        gemini_history = []
        for msg in self.conversation_history[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        chat = self.client.start_chat(history=gemini_history)
        response = chat.send_message(
            self.conversation_history[-1]["content"], stream=True
        )

        full_response = ""
        for chunk in response:
            text = chunk.text
            full_response += text
            yield text
        self._update_history("assistant", full_response)

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class OpenAIRuntimeState:
    client: Any | None = None
    active_chat_model: str | None = None


OPENAI_RUNTIME = OpenAIRuntimeState()

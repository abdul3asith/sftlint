"""Sample and ParseError data structures.

A Sample is one (prompt, response) pair produced from the dataset.
A single JSONL line can produce multiple Samples if it contains a multi-turn
conversation — each (user, assistant) pair becomes its own Sample.

A ParseError is emitted when a JSONL line fails to parse as JSON. We still
want to report on broken lines, so we yield this sentinel instead of crashing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Turn:
    """A single message in a conversation.

    Used inside Sample.history to give detectors access to prior context
    when they need it (e.g., relevance checks). Frozen so it can't be
    mutated by detectors — keeps things predictable.
    """

    role: str  # "user", "assistant", "system", "tool", etc.
    content: str


@dataclass(slots=True)
class Sample:
    """A normalized (prompt, response) pair ready for detector checks.

    Both Format A ({"prompt": ..., "response": ...}) and Format B
    ({"messages": [...]}) get normalized into this shape. Detectors
    only ever see Samples — they don't care about the input format.

    Attributes:
        sample_id: Unique identifier. Format: "line_{N}_turn_{M}".
        line_number: 1-indexed line in the source JSONL file.
        turn_index: 0-indexed position of this turn within its conversation.
            0 means single-turn or the first turn of a multi-turn conversation.
        prompt: The user message that the response is replying to.
        response: The assistant message we're auditing.
        system: Optional system prompt for the conversation (None if not present).
        history: Prior turns in the conversation (empty for single-turn).
        raw: The original parsed JSON object for this line. Detectors that need
            access to the unprocessed data (e.g., to flag extra fields) read this.
    """

    sample_id: str
    line_number: int
    turn_index: int
    prompt: str
    response: str
    system: str | None = None
    history: list[Turn] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ParseError:
    """Emitted when a JSONL line cannot be parsed as JSON.

    The format detector consumes these and turns them into Issues. Other
    detectors ignore them — you can't check structure of something that
    isn't valid JSON in the first place.

    Attributes:
        line_number: 1-indexed line in the source file.
        raw_line: The original bytes of the line (truncated for safety).
        reason: Human-readable parse error message.
    """

    line_number: int
    raw_line: str
    reason: str


# Type alias for what the dataset loader yields.
# A line can produce one ParseError, or one-or-more Samples.
DatasetRecord = Sample | ParseError

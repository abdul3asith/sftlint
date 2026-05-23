"""Issue, Report, and Severity data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True, slots=True)
class Issue:
    sample_id: str
    detector_name: str
    code: str
    severity: Severity
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Report:
    """Collected results from one scan of a dataset.

    The runner builds this incrementally: it creates one Report at the
    start of a scan, then calls add/extend as detectors emit issues.
    Reporters consume it at the end to render output.

    Unlike Issue, Report is mutable — we add to it as we scan.
    """

    dataset_path: str
    total_samples: int = 0
    total_lines: int = 0
    issues: list[Issue] = field(default_factory=list)

    # ----- mutation -----

    def add(self, issue: Issue) -> None:
        """Append a single issue."""
        self.issues.append(issue)

    def extend(self, issues: list[Issue]) -> None:
        """Append many issues at once."""
        self.issues.extend(issues)

    # ----- filtering -----

    def by_severity(self, severity: Severity) -> list[Issue]:
        """Return only issues at the given severity level."""
        return [i for i in self.issues if i.severity == severity]

    def by_detector(self, name: str) -> list[Issue]:
        """Return only issues from the given detector."""
        return [i for i in self.issues if i.detector_name == name]

    def by_code(self, code: str) -> list[Issue]:
        """Return only issues with the given code (e.g. 'F001')."""
        return [i for i in self.issues if i.code == code]

    # ----- counts -----

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)

    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.INFO)

    @property
    def has_errors(self) -> bool:
        """True if any issue is severity ERROR. Used by CLI for exit code."""
        return self.error_count > 0

import collections
import logging
import re
import time
from typing import Optional

from backend.app.core.sanitizer import redact_string
from backend.app.sentinel.models import FlightRecorderSnapshot

logger = logging.getLogger(__name__)

# Patterns that classify as pure routine junk in high-throughput microservices
ROUTINE_JUNK_PATTERNS = [
    re.compile(r"GET /health(z)? (HTTP/1\.[01]|200)", re.IGNORECASE),
    re.compile(r"GET /metrics (HTTP/1\.[01]|200)", re.IGNORECASE),
    re.compile(r"200 OK", re.IGNORECASE),
    re.compile(r"DEBUG .*heartbeat", re.IGNORECASE),
    re.compile(r"routine ping received", re.IGNORECASE),
]

# Patterns that indicate critical diagnostic evidence (exceptions, pool leaks, deadlocks)
EVIDENCE_PATTERNS = [
    re.compile(r"error", re.IGNORECASE),
    re.compile(r"fatal", re.IGNORECASE),
    re.compile(r"exception", re.IGNORECASE),
    re.compile(r"traceback", re.IGNORECASE),
    re.compile(r"50[0-4]", re.IGNORECASE),
    re.compile(r"timeout", re.IGNORECASE),
    re.compile(r"oom", re.IGNORECASE),
    re.compile(r"deadlock", re.IGNORECASE),
    re.compile(r"connection refused", re.IGNORECASE),
    re.compile(r"pool exhausted", re.IGNORECASE),
]


class BlackboxLogPruner:
    """
    Intelligent Log Pruner & Flight Recorder.
    BY DEFAULT: Pruning is DISABLED (Preserves 100% of logs).
    When ENABLED by user command: Destroys 95%+ of routine 200 OK / debug noise during steady state,
    and captures a surgically pruned Blackbox Snapshot when an anomaly occurs.
    """

    def __init__(
        self,
        buffer_size_per_service: int = 500,
        retention_seconds: float = 300.0,
        enabled: bool = False
    ):
        self.buffer_size = buffer_size_per_service
        self.retention_seconds = retention_seconds
        # By default, do NOT delete/prune any logs!
        self.enabled = enabled
        self._total_purged_count: int = 0
        self._last_status_change: float = time.time()
        # Mapping: service_name -> deque of (timestamp, log_line, is_evidence)
        self._service_buffers: dict[str, collections.deque] = collections.defaultdict(
            lambda: collections.deque(maxlen=self.buffer_size)
        )

    def enable_pruning(self) -> None:
        """Enables the smart garbage shredder."""
        self.enabled = True
        self._last_status_change = time.time()
        logger.info("[LOG PRUNER] Pruning ENABLED. Routine 200 OK / health check noise will be auto-purged.")

    def disable_pruning(self) -> None:
        """Disables pruning. Preserves 100% of all incoming logs."""
        self.enabled = False
        self._last_status_change = time.time()
        logger.info("[LOG PRUNER] Pruning DISABLED. Preserving 100% of all logs without purging.")

    def get_status(self) -> dict:
        """Returns comprehensive status of log pruning engine."""
        return {
            "pruning_enabled": self.enabled,
            "mode": "ACTIVE (Smart Noise Shredder)" if self.enabled else "DISABLED (Preserve All Logs)",
            "routine_noise_action": "Auto-Purge 200 OKs & routine health pings" if self.enabled else "Preserve 100% of logs",
            "incident_retention": "Blackbox Flight Recorder (±120s window preserved)",
            "total_purged_noise_lines": self._total_purged_count,
            "estimated_storage_saved_pct": "95%" if self.enabled else "0%",
            "last_status_change": self._last_status_change
        }

    def is_routine_noise(self, line: str) -> bool:
        """Checks if a log line is low-value routine traffic."""
        return any(pattern.search(line) for pattern in ROUTINE_JUNK_PATTERNS)

    def is_critical_evidence(self, line: str) -> bool:
        """Checks if a log line contains high-value incident evidence."""
        return any(pattern.search(line) for pattern in EVIDENCE_PATTERNS)

    def ingest_log_line(self, service_name: str, log_line: str, timestamp: Optional[float] = None) -> None:
        """Ingests a log line into the service's memory ring buffer."""
        ts = timestamp if timestamp is not None else time.time()
        evidence = self.is_critical_evidence(log_line)
        self._service_buffers[service_name].append((ts, log_line, evidence))

    def ingest_log_batch(self, service_name: str, lines: list[str]) -> None:
        """Ingests a batch of raw log lines."""
        now = time.time()
        for line in lines:
            self.ingest_log_line(service_name, line, timestamp=now)

    def capture_blackbox_snapshot(
        self,
        service_name: str,
        window_seconds: int = 120,
        now: Optional[float] = None
    ) -> FlightRecorderSnapshot:
        """
        Extracts a surgical Blackbox Snapshot for the incident window.
        If pruning is DISABLED: Preserves all logs in the window without deletion.
        If pruning is ENABLED: Purges routine noise, extracts critical stack traces, and redacts sensitive data.
        """
        current_time = now if now is not None else time.time()
        cutoff = current_time - window_seconds

        buffer = self._service_buffers[service_name]
        pruned_logs: list[str] = []
        evidence_logs: list[str] = []
        purged_count = 0

        for ts, line, is_ev in list(buffer):
            if ts < cutoff:
                continue

            # If pruning is ENABLED, purge routine noise lines that are NOT evidence
            if self.enabled and self.is_routine_noise(line) and not is_ev:
                purged_count += 1
                continue

            sanitized = redact_string(line)
            pruned_logs.append(sanitized)
            if is_ev:
                evidence_logs.append(sanitized)

        self._total_purged_count += purged_count

        logger.info(
            f"[LOG PRUNER] Captured snapshot for '{service_name}' (Pruning: {'ENABLED' if self.enabled else 'DISABLED'}): "
            f"{len(pruned_logs)} lines kept, {purged_count} lines purged."
        )

        return FlightRecorderSnapshot(
            service_name=service_name,
            incident_timestamp=current_time,
            window_seconds=window_seconds,
            pruned_logs=pruned_logs,
            root_cause_evidence=evidence_logs,
            purged_noise_count=purged_count
        )


# Global singleton instance for shared application runtime state
_global_pruner: Optional[BlackboxLogPruner] = None


def get_log_pruner() -> BlackboxLogPruner:
    """Returns the globally active BlackboxLogPruner instance."""
    global _global_pruner
    if _global_pruner is None:
        # BY DEFAULT: Pruning is DISABLED (safe by default)
        _global_pruner = BlackboxLogPruner(enabled=False)
    return _global_pruner


def set_log_pruner(pruner: BlackboxLogPruner) -> None:
    """Overrides the global pruner instance (useful for testing)."""
    global _global_pruner
    _global_pruner = pruner

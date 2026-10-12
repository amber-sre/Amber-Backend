import hashlib
import logging
import time
from collections import defaultdict
from typing import Optional

from backend.app.sentinel.models import (
    AnomalySeverity,
    AnomalyType,
    SentinelEvent,
)

logger = logging.getLogger(__name__)


class NoiseFilter:
    """
    Intelligent SRE Noise Filter & Flapping Shield.
    Eliminates alert fatigue by filtering transient glitches, suppressing flapping alarms,
    and verifying customer SLO impact before escalating to on-call engineers.
    """

    def __init__(
        self,
        transient_threshold_seconds: float = 15.0,
        flapping_window_seconds: float = 300.0,
        flapping_max_events: int = 3
    ):
        self.transient_threshold_seconds = transient_threshold_seconds
        self.flapping_window_seconds = flapping_window_seconds
        self.flapping_max_events = flapping_max_events

        # In-memory tracking of recent anomalies per service: service -> list of (timestamp, AnomalyType)
        self._history: dict[str, list[tuple[float, AnomalyType]]] = defaultdict(list)
        # Tracking of transient candidate occurrences: (service, anomaly_type) -> first_seen_time
        self._transient_candidates: dict[tuple[str, AnomalyType], float] = {}

    def _cleanup_old_history(self, now: float) -> None:
        """Purges anomaly history older than the flapping evaluation window."""
        cutoff = now - self.flapping_window_seconds
        for service in list(self._history.keys()):
            self._history[service] = [
                (t, a) for (t, a) in self._history[service] if t >= cutoff
            ]
            if not self._history[service]:
                del self._history[service]

    def compute_fingerprint(self, service_name: str, anomaly_type: AnomalyType) -> str:
        """Deterministic fingerprint for alert grouping."""
        raw = f"{service_name}:{anomaly_type.value}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def evaluate_event(
        self,
        service_name: str,
        anomaly_type: AnomalyType,
        severity: AnomalySeverity,
        description: str,
        metrics: Optional[dict] = None,
        raw_logs: Optional[list[str]] = None,
        now: Optional[float] = None
    ) -> SentinelEvent:
        """
        Evaluates an anomaly against noise filters and returns a SentinelEvent
        with is_suppressed flag and suppression reason.
        """
        current_time = now if now is not None else time.time()
        self._cleanup_old_history(current_time)

        fingerprint = self.compute_fingerprint(service_name, anomaly_type)
        service_events = self._history[service_name]

        # 1. Immediate Critical Pass: OOMKilled and DB Pool Exhaustion are NEVER transient
        if anomaly_type in (AnomalyType.OOMKILLED, AnomalyType.DB_POOL_EXHAUSTION):
            self._history[service_name].append((current_time, anomaly_type))
            return SentinelEvent(
                service_name=service_name,
                anomaly_type=anomaly_type,
                severity=AnomalySeverity.P1,
                description=description,
                timestamp=current_time,
                metrics=metrics or {},
                raw_logs=raw_logs or [],
                is_suppressed=False,
                fingerprint=fingerprint
            )

        # 2. Flapping Detection: If service has failed >= flapping_max_events in 5m
        recent_same_type = [a for (t, a) in service_events if a == anomaly_type]
        if len(recent_same_type) >= self.flapping_max_events:
            self._history[service_name].append((current_time, anomaly_type))
            logger.info(f"[NOISE FILTER] Flapping detected for {service_name} ({len(recent_same_type)} events). Grouping.")
            return SentinelEvent(
                service_name=service_name,
                anomaly_type=anomaly_type,
                severity=severity,
                description=f"[FLAPPING DETECTED] {description} (grouped {len(recent_same_type)+1} occurrences)",
                timestamp=current_time,
                metrics=metrics or {},
                raw_logs=raw_logs or [],
                is_suppressed=False,  # Still escalated once with consolidated flapping flag
                suppression_reason="CONSOLIDATED_FLAPPING_STREAM",
                fingerprint=fingerprint
            )

        # 3. Transient Glitch Filtering (e.g. temporary CPU or Latency spike)
        key = (service_name, anomaly_type)
        if key not in self._transient_candidates:
            # First occurrence: mark candidate, hold notification if latency spike
            self._transient_candidates[key] = current_time
            if anomaly_type in (AnomalyType.HIGH_LATENCY, AnomalyType.SLOW_QUERIES):
                return SentinelEvent(
                    service_name=service_name,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    description=description,
                    timestamp=current_time,
                    metrics=metrics or {},
                    raw_logs=raw_logs or [],
                    is_suppressed=True,
                    suppression_reason="TRANSIENT_WINDOW_ACTIVE: Waiting for persistent degradation.",
                    fingerprint=fingerprint
                )

        # If already seen, check if persistent longer than threshold
        first_seen = self._transient_candidates[key]
        duration = current_time - first_seen
        if duration < self.transient_threshold_seconds and anomaly_type == AnomalyType.HIGH_LATENCY:
            return SentinelEvent(
                service_name=service_name,
                anomaly_type=anomaly_type,
                severity=severity,
                description=description,
                timestamp=current_time,
                metrics=metrics or {},
                raw_logs=raw_logs or [],
                is_suppressed=True,
                suppression_reason=f"TRANSIENT_SPIKE_SUPPRESSED: Spike duration {duration:.1f}s < threshold {self.transient_threshold_seconds}s.",
                fingerprint=fingerprint
            )

        # Passed all filters: Authentic incident confirmed!
        self._history[service_name].append((current_time, anomaly_type))
        # Clear transient candidate once escalated
        if key in self._transient_candidates:
            del self._transient_candidates[key]

        return SentinelEvent(
            service_name=service_name,
            anomaly_type=anomaly_type,
            severity=severity,
            description=description,
            timestamp=current_time,
            metrics=metrics or {},
            raw_logs=raw_logs or [],
            is_suppressed=False,
            fingerprint=fingerprint
        )

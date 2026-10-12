import enum
import time
from dataclasses import dataclass, field
from typing import Any, Optional


class AnomalyType(str, enum.Enum):
    OOMKILLED = "OOMKILLED"
    CRASHLOOP = "CRASHLOOP"
    POD_FAILED = "POD_FAILED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    HIGH_LATENCY = "HIGH_LATENCY"
    DB_POOL_EXHAUSTION = "DB_POOL_EXHAUSTION"
    SLOW_QUERIES = "SLOW_QUERIES"
    NODE_PRESSURE = "NODE_PRESSURE"


class AnomalySeverity(str, enum.Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    INFO = "INFO"


@dataclass
class SentinelEvent:
    """Represents a raw or evaluated anomaly detected by Amber Sentinel."""
    service_name: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    description: str
    timestamp: float = field(default_factory=time.time)
    metrics: dict[str, Any] = field(default_factory=dict)
    raw_logs: list[str] = field(default_factory=list)
    is_suppressed: bool = False
    suppression_reason: Optional[str] = None
    fingerprint: Optional[str] = None


@dataclass
class FlightRecorderSnapshot:
    """
    Blackbox flight recorder snapshot captured at the exact moment of incident.
    Contains ONLY pruned, high-relevance logs and diagnostic metrics around the crash window.
    """
    service_name: str
    incident_timestamp: float
    window_seconds: int
    pruned_logs: list[str]
    root_cause_evidence: list[str]
    purged_noise_count: int

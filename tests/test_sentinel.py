import time
from unittest.mock import AsyncMock, patch

import pytest

from backend.app.sentinel import (
    AnomalySeverity,
    AnomalyType,
    AutonomousIncidentDispatcher,
    BlackboxLogPruner,
    NoiseFilter,
)


def test_noise_filter_immediate_critical_oom():
    filter_engine = NoiseFilter()
    event = filter_engine.evaluate_event(
        service_name="payment-service",
        anomaly_type=AnomalyType.OOMKILLED,
        severity=AnomalySeverity.P1,
        description="Container killed by OOM killer (exit code 137)"
    )
    assert event.is_suppressed is False
    assert event.severity == AnomalySeverity.P1
    assert event.anomaly_type == AnomalyType.OOMKILLED


def test_noise_filter_immediate_critical_db_saturation():
    filter_engine = NoiseFilter()
    event = filter_engine.evaluate_event(
        service_name="postgres-cluster",
        anomaly_type=AnomalyType.DB_POOL_EXHAUSTION,
        severity=AnomalySeverity.P1,
        description="Active pool connections maxed at 100/100"
    )
    assert event.is_suppressed is False
    assert event.severity == AnomalySeverity.P1


def test_noise_filter_transient_spike_suppressed():
    filter_engine = NoiseFilter(transient_threshold_seconds=15.0)
    base_time = 1000.0

    # 1. First latency spike: Held in transient candidate window
    event1 = filter_engine.evaluate_event(
        service_name="auth-service",
        anomaly_type=AnomalyType.HIGH_LATENCY,
        severity=AnomalySeverity.P2,
        description="API p99 latency spiked to 1200ms",
        now=base_time
    )
    assert event1.is_suppressed is True
    assert "TRANSIENT" in (event1.suppression_reason or "")

    # 2. 5 seconds later: Still within transient threshold (15s)
    event2 = filter_engine.evaluate_event(
        service_name="auth-service",
        anomaly_type=AnomalyType.HIGH_LATENCY,
        severity=AnomalySeverity.P2,
        description="API p99 latency spiked to 1200ms",
        now=base_time + 5.0
    )
    assert event2.is_suppressed is True

    # 3. 20 seconds later: Exceeded 15s threshold -> Persistent degradation confirmed!
    event3 = filter_engine.evaluate_event(
        service_name="auth-service",
        anomaly_type=AnomalyType.HIGH_LATENCY,
        severity=AnomalySeverity.P2,
        description="API p99 latency spiked to 1200ms",
        now=base_time + 20.0
    )
    assert event3.is_suppressed is False


def test_noise_filter_flapping_detection():
    filter_engine = NoiseFilter(flapping_max_events=3, flapping_window_seconds=300.0)
    base_time = 2000.0

    for i in range(3):
        filter_engine.evaluate_event(
            service_name="checkout-svc",
            anomaly_type=AnomalyType.CRASHLOOP,
            severity=AnomalySeverity.P1,
            description="Pod crash loop restart",
            now=base_time + (i * 10)
        )

    # 4th event in window: Flapping shield engages!
    event4 = filter_engine.evaluate_event(
        service_name="checkout-svc",
        anomaly_type=AnomalyType.CRASHLOOP,
        severity=AnomalySeverity.P1,
        description="Pod crash loop restart",
        now=base_time + 40
    )
    assert "FLAPPING DETECTED" in event4.description
    assert event4.suppression_reason == "CONSOLIDATED_FLAPPING_STREAM"


def test_log_pruner_default_disabled_preserves_all_logs():
    pruner = BlackboxLogPruner()
    assert pruner.enabled is False
    service = "orders-api"
    raw_stream = [
        "GET /healthz HTTP/1.1 200 OK",
        "DEBUG routine heartbeat received",
        "INFO 200 OK user profile fetched",
    ]
    pruner.ingest_log_batch(service, raw_stream)
    snapshot = pruner.capture_blackbox_snapshot(service, window_seconds=60)
    # By default, zero logs are purged
    assert snapshot.purged_noise_count == 0
    assert len(snapshot.pruned_logs) == 3


def test_log_pruner_purges_routine_noise_when_enabled():
    pruner = BlackboxLogPruner()
    pruner.enable_pruning()
    assert pruner.enabled is True
    service = "orders-api"

    raw_stream = [
        "GET /healthz HTTP/1.1 200 OK - 0.2ms",
        "GET /health HTTP/1.1 200 OK - 0.1ms",
        "GET /metrics HTTP/1.1 200 OK",
        "DEBUG routine heartbeat received",
        "INFO 200 OK user profile fetched",
        "ERROR Failed to connect to payment database: connection pool exhausted password=secret_token_123",
        "FATAL Thread panicked at order_dispatcher.rs:42: nil pointer dereference",
        "GET /healthz HTTP/1.1 200 OK",
    ]

    pruner.ingest_log_batch(service, raw_stream)
    snapshot = pruner.capture_blackbox_snapshot(service, window_seconds=60)

    # Purged routine 200 OKs
    assert snapshot.purged_noise_count >= 4
    # Preserved critical diagnostic evidence
    assert len(snapshot.root_cause_evidence) == 2
    # Sensitive tokens redacted
    combined = " ".join(snapshot.pruned_logs)
    assert "secret_token_123" not in combined
    assert "[REDACTED" in combined or "secret_token" not in combined


@pytest.mark.asyncio
async def test_autonomous_dispatcher():
    filter_engine = NoiseFilter()
    pruner = BlackboxLogPruner()
    service = "inventory-service"

    pruner.ingest_log_line(service, "FATAL: Postgres out of memory allocating 4GB buffer")
    event = filter_engine.evaluate_event(
        service_name=service,
        anomaly_type=AnomalyType.OOMKILLED,
        severity=AnomalySeverity.P1,
        description="Inventory service crashed with OOM"
    )
    snapshot = pruner.capture_blackbox_snapshot(service)

    with patch("backend.app.sentinel.dispatcher.process_alert_into_incident") as mock_proc:
        alert_id = await AutonomousIncidentDispatcher.dispatch_event(event, snapshot)
        assert alert_id is not None

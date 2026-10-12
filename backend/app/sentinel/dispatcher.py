import asyncio
import logging
from typing import Any

from backend.app.agents.processor import process_alert_into_incident
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.alert import Alert, AlertSource
from backend.app.sentinel.models import FlightRecorderSnapshot, SentinelEvent

logger = logging.getLogger(__name__)


class AutonomousIncidentDispatcher:
    """
    In-Process Incident Dispatcher for Amber Sovereign SRE.
    Bypasses external webhooks, ingests verified Sentinel events directly into the
    database, and triggers the LangGraph multi-agent remediation loop.
    """

    @staticmethod
    async def dispatch_event(
        event: SentinelEvent,
        snapshot: FlightRecorderSnapshot
    ) -> Any:
        """
        Creates an internal Alert record and invokes the autonomous LangGraph pipeline.
        """
        logger.info(
            f"[SENTINEL DISPATCHER] Engaging autonomous remediation for {event.service_name} "
            f"[{event.anomaly_type.value}] - Severity: {event.severity.value}"
        )

        raw_payload = {
            "source": "AMBER_SENTINEL_NATIVE",
            "service": event.service_name,
            "title": event.description,
            "anomaly_type": event.anomaly_type.value,
            "severity": event.severity.value,
            "metrics": event.metrics,
            "pruned_logs": snapshot.pruned_logs,
            "evidence": snapshot.root_cause_evidence,
            "purged_noise_count": snapshot.purged_noise_count,
            "timestamp": event.timestamp
        }

        fingerprint = event.fingerprint or f"sentinel-{event.service_name}-{event.anomaly_type.value}"

        try:
            async with AsyncSessionLocal() as session:
                alert = Alert(
                    source=AlertSource.GENERIC,
                    source_alert_id=f"sentinel-{int(event.timestamp)}",
                    title=f"[SOVEREIGN SRE] {event.service_name}: {event.anomaly_type.value}",
                    raw_payload=raw_payload,
                    fingerprint=fingerprint,
                )
                session.add(alert)
                await session.commit()
                await session.refresh(alert)
                alert_id = alert.id

            # Trigger background autonomous incident pipeline in-process
            asyncio.create_task(
                process_alert_into_incident(
                    alert_id=alert_id,
                    source="AMBER_SENTINEL",
                    raw_payload=raw_payload
                )
            )

            logger.info(f"[SENTINEL DISPATCHER] Successfully queued LangGraph pipeline for Alert {alert_id}")
            return alert_id
        except Exception as e:
            logger.error(f"[SENTINEL DISPATCHER] Failed to dispatch Sentinel event: {e}")
            return None

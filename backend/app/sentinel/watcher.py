import asyncio
import logging
import time
from typing import Optional

from sqlalchemy import text

from backend.app.core.database import AsyncSessionLocal
from backend.app.infra_providers.factory import get_infra_provider
from backend.app.sentinel.dispatcher import AutonomousIncidentDispatcher
from backend.app.sentinel.log_pruner import BlackboxLogPruner, get_log_pruner
from backend.app.sentinel.models import (
    AnomalySeverity,
    AnomalyType,
)
from backend.app.sentinel.noise_filter import NoiseFilter

logger = logging.getLogger(__name__)


class SentinelWatcher:
    """
    24x7 Sovereign Sentinel Daemon.
    Continuously monitors infrastructure health, database connection saturation,
    and service telemetry without requiring external alerts.
    """

    def __init__(
        self,
        poll_interval_seconds: float = 10.0,
        noise_filter: Optional[NoiseFilter] = None,
        log_pruner: Optional[BlackboxLogPruner] = None,
        monitored_services: Optional[list[str]] = None
    ):
        self.poll_interval = poll_interval_seconds
        self.noise_filter = noise_filter or NoiseFilter()
        self.log_pruner = log_pruner or get_log_pruner()
        self.monitored_services = monitored_services or ["payment-service", "checkout-svc", "auth-svc"]
        self._is_running = False
        self._task: Optional[asyncio.Task] = None

    async def check_database_saturation(self) -> None:
        """Inspects database active connection pool and slow transactions."""
        try:
            async with AsyncSessionLocal() as session:
                is_pg = session.bind and "postgresql" in session.bind.dialect.name
                if not is_pg:
                    return

                res = await session.execute(text("SELECT count(*) FROM pg_stat_activity WHERE state IS NOT NULL;"))
                active = res.scalar() or 0
                max_res = await session.execute(text("SHOW max_connections;"))
                max_val = max_res.scalar()
                max_conn = int(max_val) if max_val else 100

                utilization = (active / max_conn) * 100
                if utilization >= 90.0:
                    event = self.noise_filter.evaluate_event(
                        service_name="postgres-primary",
                        anomaly_type=AnomalyType.DB_POOL_EXHAUSTION,
                        severity=AnomalySeverity.P1,
                        description=f"Database pool saturated: {active}/{max_conn} ({utilization:.1f}% capacity)",
                        metrics={"active_connections": active, "max_connections": max_conn, "utilization_pct": utilization}
                    )
                    if not event.is_suppressed:
                        snapshot = self.log_pruner.capture_blackbox_snapshot("postgres-primary")
                        await AutonomousIncidentDispatcher.dispatch_event(event, snapshot)
        except Exception as e:
            logger.debug(f"[SENTINEL] Database health probe skipped: {e}")

    async def check_orchestrator_services(self) -> None:
        """Inspects container / pod health across active infrastructure provider."""
        provider = get_infra_provider()
        for service in self.monitored_services:
            try:
                health = await provider.check_service_health(service_name=service)
                status = health.get("status", "").upper()
                is_healthy = health.get("healthy", True)

                # Fetch real-time logs and stream into log pruner
                logs = await provider.fetch_service_logs(service_name=service, tail_lines=20)
                self.log_pruner.ingest_log_batch(service, logs)

                if not is_healthy or status in ("OOMKILLED", "CRASHLOOP", "FAILED"):
                    anomaly = AnomalyType.OOMKILLED if status == "OOMKILLED" else AnomalyType.CRASHLOOP
                    event = self.noise_filter.evaluate_event(
                        service_name=service,
                        anomaly_type=anomaly,
                        severity=AnomalySeverity.P1,
                        description=f"Service '{service}' degraded in {provider.provider_type.value}: Status {status}",
                        metrics=health,
                        raw_logs=logs
                    )
                    if not event.is_suppressed:
                        snapshot = self.log_pruner.capture_blackbox_snapshot(service)
                        await AutonomousIncidentDispatcher.dispatch_event(event, snapshot)
            except Exception as e:
                logger.debug(f"[SENTINEL] Error probing service '{service}': {e}")

    async def _run_loop(self) -> None:
        """The 24x7 non-sleeping Sentinel heartbeat loop."""
        logger.info(f"[SENTINEL DAEMON] Heartbeat active. Polling interval: {self.poll_interval}s")
        while self._is_running:
            try:
                await self.check_database_saturation()
                await self.check_orchestrator_services()
            except Exception as e:
                logger.error(f"[SENTINEL DAEMON] Exception in heartbeat iteration: {e}")
            await asyncio.sleep(self.poll_interval)

    def start(self) -> None:
        """Starts the Sentinel daemon as a background asyncio task."""
        if not self._is_running:
            self._is_running = True
            self._task = asyncio.create_task(self._run_loop())
            logger.info("[SENTINEL DAEMON] Started background sentinel supervisor")

    async def stop(self) -> None:
        """Gracefully halts the Sentinel daemon."""
        if self._is_running:
            self._is_running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            logger.info("[SENTINEL DAEMON] Stopped background sentinel supervisor")

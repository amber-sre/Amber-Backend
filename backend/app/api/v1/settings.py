import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import update

from backend.app.auth.security import AuthenticatedUser, require_api_key
from backend.app.core.database import AsyncSessionLocal
from backend.app.core.kill_switch import kill_switch
from backend.app.models.tool_invocation import InvocationStatus, ToolInvocation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.post("/kill-switch")
async def engage_kill_switch(
    _current_user: AuthenticatedUser = Depends(require_api_key),
) -> dict[str, Any]:
    """
    Emergency Kill-Switch. Immediately downgrades Amber to Read-Only Observation Mode.
    All queued mutating actions are instantaneously canceled.
    """
    kill_switch.engage()
    
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(ToolInvocation)
                .where(ToolInvocation.status == InvocationStatus.PENDING_APPROVAL)
                .values(
                    status=InvocationStatus.REJECTED,
                    error_message="REJECTED_BY_KILL_SWITCH: System is in Read-Only Observation Mode.",
                    executed_at=datetime.now(timezone.utc)
                )
            )
            await session.commit()
    except Exception as e:
        logger.error(f"Failed to bulk-reject pending invocations during kill-switch engagement: {e}")

    return {
        "status": "engaged",
        "message": "🚨 Amber Engine downgraded to Read-Only Observation Mode.",
        "latency_guarantee": "< 250ms"
    }

@router.delete("/kill-switch")
async def disengage_kill_switch(
    _current_user: AuthenticatedUser = Depends(require_api_key),
) -> dict[str, Any]:
    """
    Disengage the emergency Kill-Switch and resume autonomous operations.
    """
    kill_switch.disengage()
    return {
        "status": "disengaged",
        "message": "✅ Normal operations resumed."
    }

@router.get("/kill-switch/status")
async def kill_switch_status(
    _current_user: AuthenticatedUser = Depends(require_api_key),
) -> dict[str, Any]:
    return {
        "engaged": kill_switch.is_engaged
    }


@router.post("/log-pruning/enable")
async def enable_log_pruning(
    _current_user: AuthenticatedUser = Depends(require_api_key),
) -> dict[str, Any]:
    """
    Explicitly enables Smart Log Pruning. Routine noise (200 OKs, health checks)
    will be purged while blackbox error windows are preserved.
    """
    from backend.app.sentinel.log_pruner import get_log_pruner
    pruner = get_log_pruner()
    pruner.enable_pruning()
    return {
        "status": "enabled",
        "message": "🔥 Smart Log Pruning ENABLED. Routine 200 OKs & heartbeat noise will be auto-purged.",
        "details": pruner.get_status()
    }


@router.post("/log-pruning/disable")
async def disable_log_pruning(
    _current_user: AuthenticatedUser = Depends(require_api_key),
) -> dict[str, Any]:
    """
    Disables log pruning. Reverts Amber to preserving 100% of all incoming logs.
    """
    from backend.app.sentinel.log_pruner import get_log_pruner
    pruner = get_log_pruner()
    pruner.disable_pruning()
    return {
        "status": "disabled",
        "message": "🛡️ Smart Log Pruning DISABLED. Preserving 100% of logs without deletion.",
        "details": pruner.get_status()
    }


@router.get("/log-pruning/status")
async def log_pruning_status(
    _current_user: AuthenticatedUser = Depends(require_api_key),
) -> dict[str, Any]:
    """
    Returns current status of log pruner and flight recorder.
    """
    from backend.app.sentinel.log_pruner import get_log_pruner
    return get_log_pruner().get_status()


@router.get("/system-status")
async def consolidated_system_status(
    _current_user: AuthenticatedUser = Depends(require_api_key),
) -> dict[str, Any]:
    """
    Returns complete sovereign Amber SRE system status.
    """
    from backend.app.infra_providers.factory import get_infra_provider
    from backend.app.sentinel.log_pruner import get_log_pruner

    provider = get_infra_provider()
    pruner = get_log_pruner()

    return {
        "amber_version": "0.1.0",
        "sovereign_sre": "ACTIVE",
        "infra_provider": provider.provider_type.value,
        "kill_switch_engaged": kill_switch.is_engaged,
        "log_pruning": pruner.get_status(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


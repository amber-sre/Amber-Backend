from unittest.mock import AsyncMock, patch

import pytest

from backend.app.infra_providers import (
    AWSECSProvider,
    DockerProvider,
    KubernetesProvider,
    NomadProvider,
    ProviderType,
    SystemdProvider,
    detect_infrastructure_provider,
    get_infra_provider,
    set_infra_provider,
)
from backend.app.tools.remediation import (
    RestartServicePod,
    RollbackDeployment,
    RolloutRestartDeployment,
)


@pytest.mark.asyncio
async def test_infra_provider_factory_auto_detect():
    with patch("os.getenv", return_value="docker"):
        provider = await detect_infrastructure_provider()
        assert provider.provider_type == ProviderType.DOCKER

    with patch("os.getenv", return_value="aws_ecs"):
        provider = await detect_infrastructure_provider()
        assert provider.provider_type == ProviderType.AWS_ECS

    with patch("os.getenv", return_value="nomad"):
        provider = await detect_infrastructure_provider()
        assert provider.provider_type == ProviderType.NOMAD

    with patch("os.getenv", return_value="systemd"):
        provider = await detect_infrastructure_provider()
        assert provider.provider_type == ProviderType.SYSTEMD


@pytest.mark.asyncio
async def test_docker_provider_lifecycle():
    docker = DockerProvider()
    assert docker.provider_type == ProviderType.DOCKER

    # Health check
    health = await docker.check_service_health(service_name="payment-container")
    assert "healthy" in health
    assert "ready_replicas" in health

    # Logs
    logs = await docker.fetch_service_logs(service_name="payment-container", tail_lines=10)
    assert isinstance(logs, list)

    # Container restart
    restart = await docker.restart_service_instance(service_name="payment-container")
    assert restart["status"] == "CONTAINER_RESTART_TRIGGERED"

    # Swarm rollout & rollback
    rollout = await docker.rollout_restart_service(service_name="payment-container")
    assert "status" in rollout

    rollback = await docker.rollback_service(service_name="payment-container")
    assert "status" in rollback


@pytest.mark.asyncio
async def test_systemd_provider_lifecycle():
    systemd = SystemdProvider()
    assert systemd.provider_type == ProviderType.SYSTEMD

    health = await systemd.check_service_health(service_name="amber-backend")
    assert "healthy" in health

    logs = await systemd.fetch_service_logs(service_name="amber-backend", tail_lines=5)
    assert isinstance(logs, list)

    restart = await systemd.restart_service_instance(service_name="amber-backend")
    assert restart["status"] == "SYSTEMD_SERVICE_RESTARTED"


@pytest.mark.asyncio
async def test_aws_ecs_provider_lifecycle():
    ecs = AWSECSProvider(cluster_name="prod-cluster")
    assert ecs.provider_type == ProviderType.AWS_ECS

    health = await ecs.check_service_health(service_name="checkout-svc")
    assert health["healthy"] is True
    assert health["cluster"] == "prod-cluster"

    restart = await ecs.restart_service_instance(service_name="checkout-svc", instance_id="task-1234")
    assert restart["status"] == "ECS_TASK_STOPPED_AND_REPLACED"

    rollout = await ecs.rollout_restart_service(service_name="checkout-svc")
    assert rollout["status"] == "ECS_FORCE_NEW_DEPLOYMENT_TRIGGERED"

    rollback = await ecs.rollback_service(service_name="checkout-svc", target_revision="checkout:v2")
    assert rollback["status"] == "ECS_TASK_DEFINITION_ROLLED_BACK"


@pytest.mark.asyncio
async def test_nomad_provider_lifecycle():
    nomad = NomadProvider(nomad_addr="http://127.0.0.1:4646")
    assert nomad.provider_type == ProviderType.NOMAD

    health = await nomad.check_service_health(service_name="api-gateway")
    assert health["healthy"] is True

    restart = await nomad.restart_service_instance(service_name="api-gateway", instance_id="alloc-99")
    assert restart["status"] == "NOMAD_ALLOC_RESTARTED"

    rollout = await nomad.rollout_restart_service(service_name="api-gateway")
    assert rollout["status"] == "NOMAD_ROLLOUT_RESTART_DISPATCHED"

    rollback = await nomad.rollback_service(service_name="api-gateway")
    assert rollback["status"] == "NOMAD_JOB_REVERTED_TO_PRIOR_VERSION"


@pytest.mark.asyncio
async def test_remediation_tools_dispatch_via_docker_provider():
    docker_provider = DockerProvider()
    set_infra_provider(docker_provider)

    try:
        # 1. Test RestartServicePod
        tool_restart = RestartServicePod()
        res_restart = await tool_restart.execute(pod_name="redis-cache", namespace="production")
        assert res_restart.success is True
        assert res_restart.data["status"] == "CONTAINER_RESTART_TRIGGERED"

        # 2. Test RolloutRestartDeployment
        tool_rollout = RolloutRestartDeployment()
        res_rollout = await tool_rollout.execute(deployment_name="checkout-svc", namespace="production")
        assert res_rollout.success is True

        # 3. Test RollbackDeployment
        tool_rollback = RollbackDeployment()
        res_rollback = await tool_rollback.execute(deployment_name="checkout-svc", namespace="production")
        assert res_rollback.success is True
    finally:
        # Reset back to KubernetesProvider default
        set_infra_provider(KubernetesProvider())

import logging
import os
from typing import Optional

from backend.app.infra_providers.aws_ecs_provider import AWSECSProvider
from backend.app.infra_providers.base import (
    BaseInfraProvider,
    ProviderType,
)
from backend.app.infra_providers.docker_provider import DockerProvider
from backend.app.infra_providers.k8s_provider import KubernetesProvider
from backend.app.infra_providers.nomad_provider import NomadProvider
from backend.app.infra_providers.systemd_provider import SystemdProvider

logger = logging.getLogger(__name__)

_active_provider: Optional[BaseInfraProvider] = None


async def detect_infrastructure_provider() -> BaseInfraProvider:
    """
    Intelligently inspects the runtime environment and returns the best matching
    Infrastructure Provider (Kubernetes -> Docker -> AWS ECS -> Nomad -> Systemd).
    """
    explicit = os.getenv("AMBER_INFRA_PROVIDER", "").strip().lower()

    if explicit == "docker" or explicit == "docker_swarm":
        logger.info("[INFRA FACTORY] Using explicitly configured DockerProvider")
        return DockerProvider()
    elif explicit == "aws_ecs":
        logger.info("[INFRA FACTORY] Using explicitly configured AWSECSProvider")
        return AWSECSProvider()
    elif explicit == "nomad":
        logger.info("[INFRA FACTORY] Using explicitly configured NomadProvider")
        return NomadProvider()
    elif explicit == "systemd":
        logger.info("[INFRA FACTORY] Using explicitly configured SystemdProvider")
        return SystemdProvider()
    elif explicit == "kubernetes" or explicit == "k8s":
        logger.info("[INFRA FACTORY] Using explicitly configured KubernetesProvider")
        return KubernetesProvider()

    # Dynamic Auto-Detection:
    # 1. Check Kubernetes first (Kubernetes in-cluster pod or local kubeconfig)
    k8s = KubernetesProvider()
    if await k8s.is_available():
        logger.info("[INFRA FACTORY] Auto-detected active Kubernetes cluster environment")
        return k8s

    # 2. Check Docker socket
    docker = DockerProvider()
    if await docker.is_available():
        logger.info("[INFRA FACTORY] Auto-detected active Docker runtime environment")
        return docker

    # 3. Check AWS ECS
    aws = AWSECSProvider()
    if await aws.is_available():
        logger.info("[INFRA FACTORY] Auto-detected AWS ECS environment")
        return aws

    # 4. Check Nomad
    nomad = NomadProvider()
    if await nomad.is_available():
        logger.info("[INFRA FACTORY] Auto-detected HashiCorp Nomad environment")
        return nomad

    # 5. Check Linux Systemd
    systemd = SystemdProvider()
    if await systemd.is_available():
        logger.info("[INFRA FACTORY] Auto-detected Linux host with Systemd")
        return systemd

    # Default to KubernetesProvider (mock/fallback-tolerant)
    logger.info("[INFRA FACTORY] Defaulting to KubernetesProvider (standard SRE core)")
    return k8s


def get_infra_provider() -> BaseInfraProvider:
    """Returns the globally active infrastructure provider instance."""
    global _active_provider
    if _active_provider is None:
        # Default initialization (sync fallback)
        explicit = os.getenv("AMBER_INFRA_PROVIDER", "").strip().lower()
        if explicit in ("docker", "docker_swarm"):
            _active_provider = DockerProvider()
        elif explicit == "aws_ecs":
            _active_provider = AWSECSProvider()
        elif explicit == "nomad":
            _active_provider = NomadProvider()
        elif explicit == "systemd":
            _active_provider = SystemdProvider()
        else:
            _active_provider = KubernetesProvider()
    return _active_provider


def set_infra_provider(provider: BaseInfraProvider) -> None:
    """Explicitly override the active infrastructure provider (useful for testing)."""
    global _active_provider
    _active_provider = provider
    logger.info(f"[INFRA FACTORY] Active provider explicitly set to {provider.provider_type.value}")

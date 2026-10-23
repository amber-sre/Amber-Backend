import enum
from abc import ABC, abstractmethod
from typing import Any, Optional


class ProviderType(str, enum.Enum):
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    DOCKER_SWARM = "docker_swarm"
    AWS_ECS = "aws_ecs"
    NOMAD = "nomad"
    SYSTEMD = "systemd"
    MOCK = "mock"


class ServiceHealthStatus(str, enum.Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRASHLOOP = "crashloop"
    OOMKILLED = "oomkilled"
    PENDING = "pending"
    UNKNOWN = "unknown"


class BaseInfraProvider(ABC):
    """
    Abstract Universal Infrastructure Provider for Amber SRE Engine.
    Unifies container & service management across Kubernetes, Docker/Swarm, AWS ECS, Nomad, and Systemd.
    """

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Returns the specific orchestrator/infrastructure type."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Checks if the provider runtime is active and accessible."""
        pass

    @abstractmethod
    async def discover_services(self, namespace: str = "default") -> list[str]:
        """
        Dynamically discovers all running containers or services managed by this provider.
        Excludes Amber's own internal management services.
        """
        pass

    @abstractmethod
    async def fetch_service_logs(
        self,
        service_name: str,
        namespace: str = "default",
        tail_lines: int = 50,
        container_id: Optional[str] = None
    ) -> list[str]:
        """Extracts recent log lines from the target service/container."""
        pass

    @abstractmethod
    async def check_service_health(
        self,
        service_name: str,
        namespace: str = "default"
    ) -> dict[str, Any]:
        """Inspects real-time service health, replica counts, and status."""
        pass

    @abstractmethod
    async def restart_service_instance(
        self,
        service_name: str,
        instance_id: Optional[str] = None,
        namespace: str = "default"
    ) -> dict[str, Any]:
        """Restarts a single pod, container, or task instance."""
        pass

    @abstractmethod
    async def rollout_restart_service(
        self,
        service_name: str,
        namespace: str = "default"
    ) -> dict[str, Any]:
        """Performs zero-downtime rolling restart of all instances of the service."""
        pass

    @abstractmethod
    async def rollback_service(
        self,
        service_name: str,
        target_revision: Optional[str] = None,
        namespace: str = "default"
    ) -> dict[str, Any]:
        """Rolls back the service to a previous stable revision."""
        pass

import logging
from typing import Any, Optional

from backend.app.core.k8s import (
    is_k8s_available,
    k8s_check_deployment_health,
    k8s_discover_deployments,
    k8s_fetch_pod_logs,
    k8s_restart_pod,
    k8s_rollback_deployment,
    k8s_rollout_restart_deployment,
)
from backend.app.infra_providers.base import (
    BaseInfraProvider,
    ProviderType,
)

logger = logging.getLogger(__name__)


class KubernetesProvider(BaseInfraProvider):
    """
    Kubernetes & K3s Orchestration Provider for Amber.
    Interacts via official Kubernetes API client for Pods, ReplicaSets, and Deployments.
    """

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.KUBERNETES

    async def is_available(self) -> bool:
        return is_k8s_available()

    async def discover_services(self, namespace: str = "default") -> list[str]:
        return k8s_discover_deployments(namespace=namespace)

    async def fetch_service_logs(
        self,
        service_name: str,
        namespace: str = "default",
        tail_lines: int = 50,
        container_id: Optional[str] = None
    ) -> list[str]:
        # In K8s, service_name or container_id can be a pod name
        pod_name = container_id or service_name
        return await k8s_fetch_pod_logs(pod_name=pod_name, namespace=namespace, tail_lines=tail_lines)

    async def check_service_health(
        self,
        service_name: str,
        namespace: str = "default"
    ) -> dict[str, Any]:
        return await k8s_check_deployment_health(deployment_name=service_name, namespace=namespace)

    async def restart_service_instance(
        self,
        service_name: str,
        instance_id: Optional[str] = None,
        namespace: str = "default"
    ) -> dict[str, Any]:
        target_pod = instance_id or service_name
        return await k8s_restart_pod(pod_name=target_pod, namespace=namespace)

    async def rollout_restart_service(
        self,
        service_name: str,
        namespace: str = "default"
    ) -> dict[str, Any]:
        return await k8s_rollout_restart_deployment(deployment_name=service_name, namespace=namespace)

    async def rollback_service(
        self,
        service_name: str,
        target_revision: Optional[str] = None,
        namespace: str = "default"
    ) -> dict[str, Any]:
        return await k8s_rollback_deployment(
            deployment_name=service_name,
            namespace=namespace,
            target_revision=target_revision
        )

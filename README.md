<div align="center">

# ⚡ AMBER
### Autonomous In-VPC SRE & Universal Infrastructure Engine

<p align="center">
  <strong>When production catches fire, Amber brings the system back to calm.</strong><br>
  Continuous Sentinel monitoring, automated log noise shredding, sub-3s triage, and verified remediation inside your private VPC.
</p>

[![Python](https://img.shields.io/badge/Python-3.10%2B-d97809?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-State_Machine-1c1917?style=flat-square&logo=langchain&logoColor=facc15)](https://github.com/langchain-ai/langgraph)
[![Tests](https://img.shields.io/badge/Pytest-84%20Passed-10b981?style=flat-square&logo=pytest&logoColor=white)](https://pytest.org)
[![Orchestrators](https://img.shields.io/badge/Drivers-K8s%20%7C%20Docker%20%7C%20ECS%20%7C%20Nomad%20%7C%20Systemd-6366f1?style=flat-square)](https://ambersre.xyz)
[![License](https://img.shields.io/badge/License-BSL_1.1-blue?style=flat-square)](LICENSE)

<br>

<p align="center">
  <a href="https://ambersre.xyz"><strong>Explore Web Platform »</strong></a> ·
  <a href="#quickstart"><strong>Quickstart Setup »</strong></a> ·
  <a href="#amber-cli-command-reference"><strong>CLI Command Reference »</strong></a> ·
  <a href="#universal-infrastructure-matrix"><strong>Universal Infra Matrix »</strong></a> ·
  <a href="#test-suite"><strong>Verified Test Suite »</strong></a>
</p>

</div>

---

<p align="center">
  <img src="docs/images/amber-hero.png" alt="Amber SRE Engine Platform" width="100%" style="border-radius: 8px; border: 1px solid rgba(0,0,0,0.1);" />
</p>

---

## What Amber Solves

Traditional observability tools split operations into two inadequate workflows:
- **Passive metric viewers** (Datadog, New Relic) that store routine 200 OK logs and charge petabyte retention fees without resolving incidents.
- **Alert dispatchers** (PagerDuty, Opsgenie) that trigger on-call escalations for transient glitches that resolve themselves seconds later.

Amber operates as an **autonomous remediation engine**:
1. **Sentinel Surveillance:** Continuous in-VPC heartbeat inspection across container runtimes, system services, and database connection pools.
2. **Noise Filter & Flapping Shield:** Rejects transient metric spikes (< 15 seconds) and merges repeated container crash loops into a single incident state.
3. **Smart Blackbox Log Pruner:** Safe-by-default (preserves 100% of logs). When enabled via `amber log-pruner enable`, it discards routine 200 OK heartbeats while freezing a surgical **±120s flight recorder crash window**.
4. **Universal Infrastructure Engine:** Built-in drivers for **Kubernetes, Docker, Docker Swarm, AWS ECS, HashiCorp Nomad, and Linux Systemd**.
5. **Deterministic Remediation:** Sub-10s automated rollbacks, container restarts, and PostgreSQL connection pool draining.

---

## 🎮 Intentionally Headless: Terminal CLI & ChatOps Control Plane

> **SRE Reality:** At 3:00 AM during a Sev-1 outage, no on-call engineer wants to fumble with complex web portals, browser tabs, or SSO authenticators.

Amber is designed from the ground up as a **Headless SRE Control Plane** across two primary operational surfaces:

1. **📱 Mobile & ChatOps Command Hub (Slack & Telegram):**
   * **Real-time Incident Cards:** Instant root-cause alert cards delivered to your team's on-call Slack channel or dedicated Telegram group.
   * **1-Click Cryptographic Approvals:** For mutating actions (container restarts, deployment rollbacks, connection terminations), on-call SREs receive the cryptographically bound SHA-256 token with inline **`⚡ 1-Click Approve`** and **`❌ Reject`** buttons.
   * **Interactive Bot Commands:** Query `/status`, `/incidents`, `/pending`, `/approve <id>`, and `/reject <id>` directly from mobile or desktop chat.

2. **💻 In-VPC Terminal CLI (`amber` binary):**
   * **Zero-Latency Cluster Management:** Run `amber status` to inspect active surveillance and infrastructure provider health.
   * **Blackbox Log Pruning:** Toggle automated noise shredding via `amber log-pruner on` / `off` without leaving your shell.
   * **Zero Browser Bloat:** All cluster configuration, setup wizards (`amber community setup`), and diagnostic checks run locally in the terminal.

3. **🌐 Web Portal (`https://ambersre.xyz`):**
   * High-level architectural documentation, fleet sizing ROI calculator, and executive reliability audit showcases. Real operational telemetry stays strictly inside your VPC.

---

## In-VPC Privacy & Zero-Telemetry Boundary

> **The Sovereign Principle:** Your infrastructure topology, credentials, queries, and logs must not leave your private VPC to train third-party models or sit in external multi-tenant storage.

Amber is designed for compliance-driven engineering teams:

* 🛡️ **Zero Telemetry Egress (0 Bytes Leaves Your Boundary):** Amber executes entirely inside your private subnet. No analytical beacons, telemetry pings, or log data leave your network.
* 🧠 **Air-Gapped Local Model Inference (Ollama):** Triage, root-cause deduction, and runbook matching execute on local hardware via open-weights models (`qwen2.5-coder:7b`, `deepseek-r1:8b`). Source code and error traces never reach external AI APIs.
* 🧼 **In-Memory Cryptographic Secret Sanitizer:** Every raw log line, stack trace, and metric payload passes through `backend/app/core/sanitizer.py` before entering the reasoning graph. JWTs, Bearer tokens, AWS keys (`AKIA...`), database credentials, private keys, and PII are stripped in microseconds.
* 🔐 **Offline Ed25519 License Verification:** Commercial subscriptions are verified locally using public-key cryptography. In air-gapped perimeters (`AIR_GAPPED=true`), the engine validates signatures with zero network verification calls.
* 🛑 **Zero Arbitrary Shell Execution:** Amber prohibits raw, unconstrained bash shells. Remediations are bound to deterministic, schema-validated runbooks with SHA-256 HMAC payload signatures and human-in-the-loop approval gates.

---

## Architecture & Technology Stack

| Component | Technology | Technical Purpose |
| :--- | :--- | :--- |
| **Sentinel Daemon** | Async Python Engine | Continuous health inspection, PostgreSQL pool saturation tracking, and LangGraph incident dispatch. |
| **Noise Filter** | In-Memory Sliding Window | Suppresses transient metric spikes and consolidates container flapping incidents. |
| **Infra Engine** | Multi-Driver Client Core | Direct integration with Kubernetes API, Docker socket, AWS ECS API, Nomad API, and Systemd D-Bus. |
| **Reasoning Engine** | LangGraph State Machine | Stateful execution nodes: Triage Node (`<3s` latency), Runbook Hybrid RAG Node, and Investigation Node. |
| **Model Inference** | Ollama (Local) + BYOK Cloud | Local-first inference with optional dual-model consensus (Claude 3.5 Sonnet, GPT-4o, Gemini 1.5 Pro). |
| **Database Remediation** | AsyncPG / SQLAlchemy | Direct inspection of `pg_stat_activity`, lock detection, and targeted termination of hanging query handles. |
| **CLI Core** | `amber` Python Executable | Command-line management: onboarding wizards, log pruner controls, and system status terminal view. |

---

## Quickstart

### Option A: Community Edition (Interactive Setup Wizard)

Deploy Amber Community Edition on any Linux host, VPS, or Kubernetes management node:

```bash
# Automated installer
curl -fsSL https://ambersre.xyz/community.sh | bash

# Or run directly if cloned:
amber community setup
```

**Community Setup Features:**
- Automated dependency verification (Docker, Python 3.10+, database drivers, local Ollama engine).
- Interactive model selector: choose between `qwen2.5-coder:7b`, `deepseek-r1:8b`, or `llama3.2:3b`.
- Star hook: opens the Amber backend GitHub repository while model weights download in the background.
- **Community Limit:** Free forever for up to **3 active nodes and 5 services** (no license key required).

---

### Option B: Commercial Edition (Enterprise Cryptographic Setup)

For production clusters and fleets requiring higher capacity:

```bash
# Automated enterprise installer
curl -fsSL https://ambersre.xyz/install.sh | bash

# Or run directly if cloned:
amber commercial setup
```

**Commercial Setup Features:**
- Single-use Ed25519 cryptographic license token verification (`amb_live_...`).
- Background model download while configuring secondary cloud provider keys.
- Direct PostgreSQL healing configuration with validated connection tests.
- High-capacity quotas and multi-cloud fleet orchestration.

---

### Option C: Docker Compose Full Stack (Self-Hosted)

Spin up the complete backend stack (FastAPI Backend, Sentinel daemon, PostgreSQL with pgvector, Redis, and Ollama) with Docker Compose:

```bash
git clone https://github.com/amber-sre/Amber-Backend.git ~/.amber
cd ~/.amber

# Start all services in the background
docker compose up -d

# Inspect status of running services
docker compose exec backend amber status
```

---

### Option D: Local Python Environment Setup

```bash
git clone https://github.com/amber-sre/Amber-Backend.git
cd Amber-Backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies in editable mode
pip install -e .

# Run test suite
pytest tests/ -v
```

---

## Amber CLI Command Reference

Amber installs a standalone `amber` binary in your PATH:

| Command | Description |
| :--- | :--- |
| `amber status` | Displays the Sovereign SRE status dashboard (Sentinel state, active model, pruner status, kill-switch). |
| `amber community setup` | Launches the interactive Community Edition onboarding wizard. |
| `amber commercial setup` | Launches the Enterprise Commercial onboarding wizard with Ed25519 key verification. |
| `amber log-pruner enable` | Engages the smart noise shredder: purges routine 200 OKs, saving ~95% log storage. |
| `amber log-pruner disable` | Reverts to safe default: preserves 100% of incoming logs without pruning. |
| `amber log-pruner status` | Outputs current pruner statistics, purged line count, and disk space saved. |

---

## Universal Infrastructure Matrix

Amber inspects its runtime environment on startup and binds the matching orchestrator driver:

| Platform | Supported Actions | Integration Method |
| :--- | :--- | :--- |
| **Kubernetes (K8s & K3s)** | Pod log capture, pod recreation, rollout restarts, deployment rollback | Official Kubernetes Python API Client (`CoreV1Api`, `AppsV1Api`) |
| **Docker & Docker Swarm** | Container logs, container restart, rolling service updates, service rollback | Unix Domain Socket `/var/run/docker.sock` / Docker SDK |
| **AWS ECS & Fargate** | CloudWatch log streaming, task replacement, forced deployment rollout | AWS Boto3 ECS API & CloudWatch Logs API |
| **HashiCorp Nomad** | Allocation log inspection, allocation restart, job version rollback | Official Nomad HTTP REST API (`/v1/job/{id}`) |
| **Linux Systemd** | `journalctl` stream capture, `systemctl restart <unit>` | Linux systemd D-Bus interface and CLI wrappers |

---

## Subscription Tiers & Predictable Economics

| Metric / Capability | Community Tier (Free Forever) | Growth Tier ($2,499/mo) | Autonomous Tier ($5,999/mo) | Sovereign Tier ($11,999/mo) |
| :--- | :--- | :--- | :--- | :--- |
| **Target Scale** | Test clusters & homelabs | Growth-stage startups | Production microservices fleets | Regulated FinTech, Banks & HealthTech |
| **Managed Nodes** | Up to 3 Active Nodes | Up to 50 Cloud / K8s Nodes | Up to 250 Cloud / K8s Nodes | Unlimited Multi-VPC Fleet Scale |
| **Production Services** | Up to 5 Services | Up to 25 Services | Unlimited Services | Unlimited Services |
| **Data Boundary** | 100% In-VPC (Zero Egress) | 100% In-VPC (Zero Egress) | 100% In-VPC (Zero Egress) | 100% In-VPC (Air-Gapped Sovereign) |
| **Sentinel Heartbeat** | Continuous 24/7 Heartbeat | Continuous 24/7 Heartbeat | Continuous 24/7 Heartbeat | Continuous 24/7 Heartbeat |
| **Noise Filtering** | Transient Glitch Shield ON | Transient Glitch Shield ON | Multi-VPC Incident Correlation | Dedicated Driver Filtering Matrix |
| **Smart Log Pruner** | Blackbox Flight Recorder (±120s) | Blackbox 60%+ Cloud Cut | 90% High-Throughput Log Cut | Air-Gapped Surgical Retention |
| **Automated Actions** | Read-Only Triage & Proof | 150 Included Mutating Actions/mo | 500 Included Mutating Actions/mo | Unlimited Autonomous Actions |
| **PR Auto-Drafting** | No | No | Verified GitHub/GitLab Bug-fix PRs | Monorepo & Bespoke Arch PRs |
| **Audits & Digests** | Markdown Post-Mortems | Markdown Post-Mortems | Weekly Ed25519 Signed PDFs | Compliance & Board Audit Packs |
| **Pricing (USD / INR)** | $0 (Free Forever) | $2,499/mo (₹2.1L/mo annual) | $5,999/mo (₹5.0L/mo annual) | $11,999/mo (₹10.0L/mo annual) |
| **Support SLA** | GitHub Community Discussions | Email & Slack Support | 4-hr SLA & Dedicated SRE Bridge | Contractual Sub-10s MTTR Guarantee |

---

## Test Suite

Amber maintains an automated test suite verifying multi-agent reasoning, infrastructure drivers, noise filters, and cryptographic controls:

```bash
pytest tests/ -v
```

```text
tests/test_approvals.py .....                                            [  5%]
tests/test_auth.py .....                                                 [ 11%]
tests/test_enterprise_sso_multicluster.py .....                          [ 17%]
tests/test_infra_providers.py ......                                     [ 25%]
tests/test_k8s.py ......                                                 [ 32%]
tests/test_license.py .......                                            [ 40%]
tests/test_llm_gateway.py ..............................                 [ 76%]
tests/test_notifications.py ...                                          [ 79%]
tests/test_post_mortem.py ..                                             [ 82%]
tests/test_sanitizer.py ....                                             [ 86%]
tests/test_sentinel.py .......                                           [ 95%]
tests/test_tools.py ....                                                 [100%]

============================== 84 passed in 8.04s ==============================
```

---

## License & Commercial Terms

Amber Backend is licensed under the **Business Source License 1.1 (BSL 1.1)**:
- **Free Community Edition:** Free forever for internal development, staging, and production clusters up to **3 active nodes and 5 services**.
- **Enterprise Commercial License:** Any deployment exceeding Community Tier limits or requiring multi-cluster automated healing requires an official Amber Enterprise License Key.
- **Commercial Inquiries:** [https://ambersre.xyz/#connect](https://ambersre.xyz/#connect) or `founders@ambersre.xyz`.

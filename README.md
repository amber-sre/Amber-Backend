<div align="center">

# ⚡ AMBER
### Autonomous Sovereign SRE & Universal Infrastructure Engine

<p align="center">
  <strong>When production catches fire, Amber brings the system back to calm.</strong><br>
  24x7 Sovereign Sentinel surveillance, zero-sleep anomaly detection, smart log noise shredding, and verified remediation — built to act when your team can’t.
</p>

[![Python](https://img.shields.io/badge/Python-3.10%2B-d97809?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-1c1917?style=for-the-badge&logo=langchain&logoColor=facc15)](https://github.com/langchain-ai/langgraph)
[![Tests](https://img.shields.io/badge/Pytest-84%20Passed-10b981?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org)
[![Universal Infra](https://img.shields.io/badge/Orchestrators-K8s%20%7C%20Docker%20%7C%20ECS%20%7C%20Nomad%20%7C%20Systemd-6366f1?style=for-the-badge)](https://ambersre.xyz)
[![Sentinel](https://img.shields.io/badge/Sentinel-24%2F7%20Zero--Sleep%20Heartbeat-ef4444?style=for-the-badge)](https://ambersre.xyz)

<br>

<p align="center">
  <a href="https://ambersre.xyz"><strong>Explore Web Platform »</strong></a> ·
  <a href="#-quickstart"><strong>Community Setup »</strong></a> ·
  <a href="#-amber-cli-command-reference"><strong>Amber CLI Reference »</strong></a> ·
  <a href="#-universal-infrastructure-engine"><strong>Universal Infra Matrix »</strong></a>
</p>

</div>

---

<p align="center">
  <img src="docs/images/amber-hero.png" alt="Amber SRE Engine Platform" width="100%" style="border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);" />
</p>

---

## 🌟 What Makes Amber Sovereign? (Amber vs All SRE)

Most DevOps tools fall into two traps: they are either **passive graph viewers** (like Datadog/New Relic) that bill you thousands of dollars to store routine 200 OK log garbage, or **noisy alert dispatchers** (like PagerDuty) that wake up engineers for temporary 5-second glitches.

Amber is the **complete autonomous replacement**:
1. **Sovereign Ingestion & Sentinel Daemon:** 24x7 in-VPC heartbeat monitor across containers, databases, and microservices. Zero third-party webhooks required.
2. **Noise Filter & Flapping Shield:** Automatically silences transient glitches (< 15s spikes) and consolidates crashing container flaps into a single actionable incident.
3. **Smart Blackbox Log Pruner:** Safe-by-default (preserves 100% of logs). When enabled via `amber log-pruner enable`, it destroys 95%+ of routine 200 OK / heartbeat noise while freezing a surgical **±120s flight recorder crash window**.
4. **Universal Infrastructure Engine:** Zero-config auto-detection for **Kubernetes, Docker, Docker Swarm, AWS ECS, HashiCorp Nomad, and Linux Systemd**.
5. **Deterministic Remediation:** Sub-60s automated rollbacks, pod recreations, and PostgreSQL hanging connection pool terminations.

---

## 🔒 100% In-VPC Privacy, Air-Gapped Operation & Zero-Telemetry Sovereignty

> **The Sovereign Principle:** Your infrastructure code, secrets, database queries, and incident logs should **NEVER** leave your VPC to train third-party models or sit in an unencrypted multi-tenant SaaS silo.

Amber is engineered specifically for security-first engineering, fintech, defense, and high-compliance teams:

* 🛡️ **Zero Telemetry Egress (0 Bytes Leaves Your VPC):** Unlike Datadog, New Relic, or cloud APMs that hoover up and bill you for petabytes of private telemetry, Amber runs 100% locally inside your private subnet. Zero analytics beacons, telemetry pings, or log data leave your boundary.
* 🧠 **Air-Gapped Local LLM Brain (Ollama):** Triage, root-cause deduction, and runbook matching run entirely on your own CPU/GPU hardware via self-hosted open-weights models (`qwen2.5-coder:7b`, `deepseek-r1:8b`). Your proprietary source code and error messages never touch external AI APIs.
* 🧼 **In-Memory Cryptographic Secret Sanitizer:** Every raw log, stack trace, and metric payload passes through Amber's high-speed in-memory sanitizer (`backend/app/core/sanitizer.py`) before reaching the reasoning mesh. All JWTs, Bearer tokens, AWS access keys (`AKIA...`), database passwords, private keys, and PII are stripped in microseconds.
* 🔐 **Offline Cryptographic License Verification (Ed25519):** Enterprise commercial licenses are validated completely offline using digital signatures and hardware bindings. The engine operates in air-gapped perimeters (`AIR_GAPPED=true`) with **zero phone-home licensing checks**.
* 🛑 **Zero Arbitrary Shell Execution:** Amber does not hand raw unrestricted bash shells to any LLM. Remediations are strictly bound to deterministic, schema-validated runbooks with SHA-256 HMAC payload signatures and human-in-the-loop approval gates.
* 🗄️ **Local Smart Blackbox Noise Shredder:** Routine 200 OK traffic is safely shredded on your own disk, preserving a high-fidelity **±120s flight recorder crash window** without forcing you to pay SaaS cloud log retention bills.

---

## 🛠️ Complete Tech Stack Matrix

| Layer | Technology | Role & Architecture Rationale |
| :--- | :--- | :--- |
| **Sovereign Sentinel** | **24x7 Async Heartbeat Daemon** | Continuous infrastructure health probes, PostgreSQL pool saturation monitoring, and zero-webhook LangGraph dispatch. |
| **Noise & Log Filter** | **Transient Shield + Blackbox Pruner** | Filters temporary metric glitches, suppresses flapping alert storms, and captures surgical error snapshots. |
| **Universal Infra** | **Multi-Orchestrator Adapter Engine** | Auto-detects runtime: native drivers for K8s (API client), Docker/Swarm (`docker.sock`), AWS ECS, Nomad, and Systemd. |
| **AI Reasoning Engine**| **LangGraph Multi-Agent Mesh** | Stateful graph orchestration: Triage Node (`<3s` latency), Hybrid RAG Node (Runbooks), and Investigation Node. |
| **LLM Inference** | **Local Ollama + Hybrid Cloud BYOK** | Local-first inference (Qwen 2.5 Coder, DeepSeek-R1) with optional secondary consensus (Claude 3.5 Sonnet, GPT-4o, Gemini). |
| **Database Remediation**| **Async PostgreSQL Driver** | Direct connection pool inspection (`pg_stat_activity`), lock detection, and hanging PID termination. |
| **Control CLI** | **`amber` CLI (Python Core)** | Single-command management: interactive setup wizards, log pruner toggling, and live system status dashboard. |

---

## 🚀 Quickstart

### Option A: Community Edition (Interactive Animated Wizard)

Deploy the fully-functional Amber Community Edition on any Linux host, VPS, or Kubernetes node:

```bash
# One-line automated setup
curl -fsSL https://ambersre.xyz/community.sh | bash

# Or directly from the repo:
amber community setup
```

**The Interactive Community Setup Wizard features:**
* 🎬 **Animated ASCII Startup:** Amber SRE kernel initialization animation.
* 📦 **Dependency Checklist with Live Progress:** Audits Docker, Python 3.10+, database drivers, orchestrator core, and local Ollama engine.
* 👤 **Operator Profile:** Collects Name, Email, VPC Name, and Startup Project Name.
* 🤖 **Interactive Arrow-Key Model Selector:** Choose between `qwen2.5-coder:7b`, `deepseek-r1:8b`, or `llama3.2:3b`.
* ⭐ **GitHub Star Hook:** Automatically opens the Amber backend repository for starring while your AI model downloads in the background.
* 🔒 **Community Quota:** Free forever for up to **3 Managed Nodes & 5 Services** (Zero License Key required).

---

### Option B: Commercial Edition (Enterprise Cryptographic Wizard)

For production fleets, multi-cluster VPCs, and unlimited node deployments:

```bash
# One-line automated enterprise setup
curl -fsSL https://ambersre.xyz/install.sh | bash

# Or directly from the repo:
amber commercial setup
```

**The Enterprise Commercial Wizard features:**
* 🔑 **Single-Use Cryptographic License Verification:** Activates Ed25519-signed license keys (`amb_live_...`), hardware-binds to machine, and displays plan validity.
* ⚡ **Dual-Screen Background Download:** Local model downloads in the background while you configure secondary keys.
* ☁️ **Hybrid Cloud AI Option:** Interactive prompt to configure Claude 3.5 Sonnet, GPT-4o, or Gemini 1.5 Pro for hybrid multi-agent consensus.
* 🗄️ **Database URL Setup:** Interactive prompt with smooth backspace/empty skip to connect direct PostgreSQL auto-healing.
* 🚀 **Unlimited Capacity:** All nodes unlocked, multi-cloud ready, and 24/7 dedicated SRE SLA.

---

### Option C: Docker Compose Full Stack (100% Self-Hosted & Air-Gapped)

Spin up the entire sovereign stack (FastAPI Backend with 24/7 Sentinel daemon, PostgreSQL 16 pgvector, Redis 7, and Ollama) with a single command:

```bash
git clone https://github.com/himanshu-xyz-1/Amber-Backend.git ~/.amber
cd ~/.amber

# Start all sovereign services in background
docker compose up -d

# Check live Sovereign Dashboard inside the container
docker compose exec backend amber status
```

---

## 💻 Amber CLI Command Reference

Amber comes with a dedicated command-line interface installed in your PATH:

| Command | Description |
| :--- | :--- |
| `amber status` | Displays full Amber Sovereign SRE Dashboard (Sentinel status, active provider, pruner state, kill-switch). |
| `amber community setup` | Runs the interactive Community Edition onboarding wizard. |
| `amber commercial setup` | Runs the interactive Enterprise Commercial onboarding wizard. |
| `amber log-pruner enable` | **Engages Smart Noise Shredder:** Auto-purges routine 200 OKs and health pings, saving ~95% log storage. |
| `amber log-pruner disable` | **Reverts to Safe Default:** Preserves 100% of all incoming logs without deletion. |
| `amber log-pruner status` | Inspects current pruner statistics, purged line count, and estimated space saved. |

---

## 🌐 Universal Infrastructure Engine Matrix

Amber automatically detects your hosting environment on boot and binds the appropriate orchestrator driver:

| Environment | Supported Actions | Execution Mechanism |
| :--- | :--- | :--- |
| **Kubernetes (K8s & K3s)** | Pod log extraction, pod recreation, rollout restart, deployment rollback | Official Kubernetes CoreV1 & AppsV1 API Client |
| **Docker & Docker Swarm** | Container logs, container restart, swarm rolling update, swarm service rollback | Unix Socket `/var/run/docker.sock` / Docker CLI |
| **AWS ECS & Fargate** | CloudWatch log streaming, task replacement, force new deployment rollout | AWS ECS API / CloudWatch Streams |
| **HashiCorp Nomad** | Allocation log inspection, allocation restart, job version rollback | Official Nomad HTTP API (`/v1/job/{id}`) |
| **Linux Bare-Metal / VPS** | `journalctl` stream capture, `systemctl restart <service>` | Linux systemd D-Bus & CLI wrappers |

---

## 📊 Subscription Tiers & Predictable Economics

| Capability | Community Tier (Free Forever) | Autonomous Tier ($2,299/mo) | Response Tier ($4,299/mo) |
| :--- | :--- | :--- | :--- |
| **Target Scale** | Indie hackers & test clusters | Growing startups & production fleets | Enterprise multi-cloud infrastructure |
| **Managed Nodes** | **Up to 3 Active Nodes** | **Up to 100 Cloud / K8s Nodes** | **Unlimited Enterprise Fleet** |
| **Production Services** | **Up to 5 Services** | **Up to 35 Services** | **Enterprise Fleet** |
| **Data Sovereignty** | **100% In-VPC (Zero Egress)** | **100% In-VPC (Zero Egress)** | **Air-Gapped & Sovereign** |
| **Sentinel Heartbeat** | 24x7 Continuous Heartbeat | 24x7 Continuous Heartbeat | 24x7 Continuous Heartbeat |
| **Noise Filtering** | Transient Glitch Shield ON | Transient Glitch Shield ON | Advanced Multi-VPC Correlation |
| **Smart Log Pruner** | Blackbox Flight Recorder (±120s) | Blackbox Flight Recorder (±120s) | Customizable Retention Policies |
| **Automated Remediations** | 10 Verified HITL Actions/mo (3 Nodes) | 100 Included Mutating Actions/mo | High-Volume (500/mo) Mutating Actions |
| **Billing Cycle** | **$0 (Zero Key Required)** | $2,299/mo (Annual) or $2,499/mo | $4,299/mo (Annual) or $4,499/mo |
| **Support SLA** | GitHub Community | Private Slack Connect | Priority Incident Bridge Escalation |
| **Contact to Upgrade** | `founders@ambersre.xyz` | [ambersre.xyz/#connect](https://ambersre.xyz/#connect) | Dedicated Forward-Deployed SRE Support |

---

## 🧪 Verifiable Production Test Suite

Amber maintains an exhaustive automated test suite covering multi-agent reasoning, infrastructure providers, noise filters, and cryptographic guardrails:

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

============================== 84 passed in 4.95s ==============================
```

---

## 📄 License & Commercial Terms

Amber Backend is licensed under the **Business Source License 1.1 (BSL 1.1)**:

- **Free Community Edition:** Free forever for internal development, testing, and production clusters up to **3 active nodes and 5 services**.
- **Enterprise Commercial License:** Any deployment exceeding Community Tier limits or requiring multi-cluster automated healing requires an official Amber Enterprise License Key.
- **Enterprise Inquiries:** [https://ambersre.xyz/#connect](https://ambersre.xyz/#connect) · `founders@ambersre.xyz`

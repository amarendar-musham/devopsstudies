# System Design — Answer Cheatsheet (DevOps / Platform / SRE)

> At senior level you design an infra/platform system and defend trade-offs. They score **structured thinking**, not a perfect answer. This file gives you a reusable framework plus **fully worked model answers** for the six prompts most likely to come up — each anchored in *your real systems* so you can speak from experience, not theory.
>
> Your unfair advantage: prompts 1, 2, and 5 are **literally your work**. Lead with the real design, then generalize.

---

## THE FRAMEWORK (say the steps out loud, every time)

1. **Clarify** — requirements, scale, SLOs, constraints. Never design blind. Ask: how many users/services/orgs? Growth? Availability target (99.9 / 99.99)? Latency? Budget / existing cloud? Compliance?
2. **Scope** — state what you WILL and WON'T cover in the time.
3. **High-level** — draw the boxes: sources → pipeline → compute → storage → observability.
4. **Deep-dive** — pick the 1–2 components they care about; go deep.
5. **Scale & failure** — bottlenecks, SPOFs, "what happens when X dies."
6. **Trade-offs** — name the alternatives you rejected and *why*.
7. **Wrap** — summarize; note what you'd add with more time.

**Cross-cutting concerns to sprinkle (signals seniority):** Reliability (redundancy, health checks, blast-radius control, canary), Observability (metrics/logs/traces, SLOs, alert on symptoms), Security (least-privilege IAM, secrets manager, private endpoints, image scanning), Cost (right-sizing, autoscaling, cleanup), Automation (IaC, GitOps, self-service).

---

# PROMPT 1 — Design a CI/CD platform for 100+ microservices

**★ This is your Oracle Commerce + Salesforce Industries work. Lead with it.**

**Clarify:** How many teams and deploy frequency? Mono vs multi-repo? Target K8s? Rollback needs? Compliance (PCI/SOC)? Continuous deployment allowed, or does the business require sign-off?

**High-level design:**
- **Source:** per-service Git repos → webhook / PR-builder triggers.
- **CI:** Jenkins with **ephemeral Kubernetes pod agents** (fresh pod per build, torn down after — clean isolation, elastic scale). Stages: build → unit test → **layered security scan (SAST + image scan + DAST)** → publish immutable artifact to a registry (OCIR/JFrog/Nexus).
- **Shared library, not copy-paste:** put common build/deploy/notify logic in a **Jenkins shared library** (`vars/*.groovy`); each service is a thin Jenkinsfile calling it. *(This is exactly how I built the Salesforce Industries platform — `globalLib` cloud-agnostic core + thin cloud-specific libs, ~90 jobs as thin wrappers, so a fix propagates everywhere.)*
- **CD:** Helm charts per service; deploy via pipeline or GitOps (ArgoCD). **Progressive rollout strategies per environment:**
  - **Dev:** rolling update (K8s default) — fast, low risk.
  - **Staging:** canary (5% → 25% → 100%) to catch issues before prod.
  - **Prod:** blue-green for zero-downtime atomic cutover + instant rollback, OR canary with automated health checks for gradual, low-risk rollout.
- **Environments:** dev → staging → prod, promotion gated by tests + approvals.
- **Observability:** pipeline metrics, deploy success rate, DORA metrics. For canary: Prometheus tracking error rate, latency (p50/p95/p99), request rate; auto-promote or auto-rollback via Flagger/Argo Rollouts or manual Grafana review.

**Deep-dive — canary/blue-green implementation (K8s + Helm):**

**Canary (with ingress controller — Nginx/Istio):**
1. Deploy new version as a separate Deployment with label `version=v2`, alongside stable `version=v1`.
2. Both selected by the same Service (or split into two Services with shared selector, depending on ingress config).
3. Configure ingress **weighted routing** — start 95% traffic to v1, 5% to v2. In Istio use VirtualService with `weight:` fields; in Nginx Ingress use `nginx.ingress.kubernetes.io/canary-*` annotations.
4. **Monitor canary metrics** (error rate, latency) vs stable baseline. Decision criteria: if canary error rate > 2x baseline OR p95 latency > 1.5x baseline → abort (set canary weight to 0%, delete Deployment). If healthy after N minutes → shift traffic (20% → 50% → 100%), scaling canary replicas up and stable down in parallel.
5. Once 100% on canary, delete the stable Deployment. The canary *becomes* the new stable.

**Blue-green (atomic cutover):**
1. Two full Deployments: `myapp-blue` (current prod) and `myapp-green` (new version), each with distinct labels (`color=blue` / `color=green`).
2. Production Service selector points at `color=blue`.
3. Deploy new version to green, wait for all pods Ready, run smoke tests (port-forward or separate test Service).
4. **Atomic switch:** `kubectl patch service myapp -p '{"spec":{"selector":{"color":"green"}}}'` — traffic cuts over instantly to green.
5. Monitor for issues; if any, **instant rollback** by patching selector back to `blue`.
6. Once green is stable, tear down blue or leave as standby for next deploy.

**Trade-off — canary vs blue-green:**
- **Canary** = gradual, observable, low blast radius, same capacity (just add a few canary pods). Best for risk mitigation when you trust your metrics.
- **Blue-green** = instant cutover, instant rollback, **2x capacity** during cutover (expensive), zero gradual observation. Best for schema changes, high-risk deploys, or when you can afford the capacity and want atomic semantics.

**Deep-dive — latency & compliance (from real work):**
- *Latency:* at Oracle I got commit-to-production-ready under **5 hours** by running **certification testing and image scanning in parallel**, and by **fanning out N provisioning jobs** and sharding test suites across environments. Parallelism is the main lever — you trade cloud cost for wall-clock time.
- *Compliance:* we deliberately chose Continuous **Delivery**, not Deployment, because production upgrades needed customer sign-off and OPS scheduling. We enforced **separation of duties** — only the Operations team could promote images to the prod registry, using a **one-time registry token** — which is how we passed PCI/SOC audits. Compliance was *designed into* the pipeline, not bolted on.

**Scale & failure:** ephemeral agents scale horizontally; a bad build is caught by scans + gates; canary limits blast radius and auto-rolls back on metric violations; blue-green gives instant rollback via selector flip; `helm rollback` reverts to any prior revision. SPOF is the Jenkins controller → HA controller + config-as-code so it's rebuildable.

**Trade-offs:** 
- **Rollout strategy:** rolling (cheapest, gradual) vs canary (observable, controllable blast radius, slight capacity overhead) vs blue-green (instant cutover/rollback, 2x capacity cost).
- **CI platform:** Jenkins (flexible, shared-library reuse, I know it deeply) vs GitLab CI (simpler, less flexible) vs pure ArgoCD GitOps (declarative, pull-based, great for CD but you still need CI). 
- **Agents:** ephemeral K8s pods (isolation + elastic scale) vs static agents (lower startup latency, higher idle cost).
- **Canary automation:** Flagger/Argo Rollouts (fully automated metric-driven promotion) vs manual Grafana review (simpler, more control, requires human in loop).

---

# PROMPT 2 — Design secrets management for an org

**★ Your Salesforce secret-rotation pipeline + GSPANN Vault work.**

**Clarify:** How many services/accounts? Rotation frequency? Cloud? Compliance? Who consumes — humans, machines, or both?

**High-level design:**
- **Central store:** HashiCorp Vault (dynamic secrets + KV) and/or cloud KMS (OCI Vault). Machine consumers pull from Vault at runtime; human/interactive access via a separate path (e.g. 1Password).
- **Rotation pipeline (my real story):** reset the credential → **validate the new credential actually authenticates** → *only after validation passes*, propagate to the stores. This **fail-closed** gate is the heart of it: you never store a broken secret. Parallelize the per-account work with a thread pool because it's **I/O-bound** (network waits, not CPU).
- **Access:** short-lived tokens, least-privilege policies, audit logging.
- **Distribution:** apps fetch at runtime — **never bake secrets into images or logs, never pass on the CLI** (CLI args leak into process listings — a rule I actually enforce, passing passwords only via env vars). In K8s use the CSI secrets driver / Vault agent injector.

**Deep-dive — the validation gate & partial-failure handling:**
- Each account rotates **independently**, so one failure doesn't halt the batch. For a failed account the store still holds the last-known-good secret, so consumers keep working on the previous credential until that one account is remediated. That's graceful degradation, not all-or-nothing.

**Failure modes:** validation gate prevents propagating broken secrets; if Vault itself is down → HA/Raft cluster + short-lived cached leases so consumers survive a brief outage.

**Trade-offs:** Vault (powerful dynamic secrets, ops overhead) vs cloud-native KMS (simpler, but lock-in). Threads vs multiprocessing — threads, because the workload is I/O-bound. Rotate-then-validate-then-propagate vs propagate-then-validate — the former is fail-closed and strictly safer.

---

# PROMPT 3 — Design a multi-region, highly available Kubernetes platform

**★ Anchor in your self-managed 3-master HA and the OKE migration.**

**Clarify:** RTO/RPO? Active-active vs active-passive? Stateful workloads? Managed (OKE/EKS) or self-managed?

**High-level design:**
- **Managed K8s (OKE/EKS) per region** with cluster autoscaler + HPA. *Prefer managed control planes* — I ran a self-managed 3-master control plane and it's a lot of operational surface (see deep-dive); moving to OKE with a managed control plane + private API endpoint + bastion removed that toil.
- **Ingress:** **per-region Ingress Controller** (Nginx/cloud-native) provisions a regional load balancer that routes HTTP/HTTPS traffic to Services based on host/path rules. Above that, a **global load balancer** (cloud CDN/global LB, or GeoDNS like Route 53 with health checks) routes users to the nearest healthy region. TLS terminates at the Ingress, certs managed by cert-manager (Let's Encrypt or internal CA).
- **State:** replicated / managed multi-region DB; object storage cross-region replication. In OCI, private endpoints + NSGs for DB access.
- **Networking:** VCN peering / DRG, private subnets, NSGs (finer-grained than security lists).
- **Delivery:** same Helm/GitOps to every region.

**Deep-dive — control-plane HA (real, hard-won detail):**
"On self-managed clusters I ran **3 masters behind a virtual IP**. A cron-driven script ran effectively every 15 seconds on each master, health-checking peers on **four dimensions**: ICMP ping, SSH (10s timeout), kube-apiserver `/healthz` on 6443, and **whether the block volume was mounted and writable**. On primary failure the next master claimed the VIP by reassigning the private IP to its own VNIC via the OCI CLI. Each master also self-rebooted if its own apiserver was down *and* storage was wedged. The block-volume check was the key lesson — we'd seen the **apiserver look healthy while storage was wedged**, a failure a naive `/healthz` check misses." This is a great story for "how do you design a health check" — a single signal isn't enough.

**Failure:** lose a region → traffic shifts via DNS/global LB; lose a node → pods reschedule; lose an AZ → multi-AZ node pools across availability domains.

**Trade-offs:** active-active (complex, low RTO, data-consistency hard) vs active-passive (simpler, higher RTO). **Managed vs self-managed control plane** — this is your signature trade-off: self-managed gives control but huge operational surface; managed reduces toil on undifferentiated heavy lifting. Consistency vs latency for multi-region state.

---

# PROMPT 4 — Design a monitoring & alerting stack (with external-metrics autoscaling)

**★ You built external-metrics HPA on Victoria Metrics — use it in the deep-dive.**

**High-level design:**
- **Metrics:** Prometheus (scrape `/metrics`) → **Grafana** dashboards → **Alertmanager** routing → PagerDuty/Slack. Logs to ELK. Long-term storage via Thanos/Cortex (or Victoria Metrics).
- **SLOs:** define **SLIs** (latency, error rate, availability), set **SLOs**, and **alert on symptoms / burn rate**, not causes — this is how you avoid alert fatigue.

**Deep-dive — HPA basics and external-metrics (real):**

"Start with **resource-based HPA** — the default. HPA queries the metrics-server every 15 seconds, compares current CPU/memory utilization to a target, and scales replicas to meet it. Formula: `desiredReplicas = ceil(currentReplicas * (currentMetric / targetMetric))`. CPU-based HPA is the workhorse — set pod CPU requests accurately, target 50-70% utilization, and HPA keeps you in that band. Memory-based HPA is trickier because memory isn't compressible — by the time HPA sees high memory and scales, pods may already be OOMKilled.

**External-metrics HPA** is where it gets powerful — I built this at Oracle. You scale on a metric **outside** the cluster: queue depth, request rate from a load balancer, custom business metrics. I drove HPA off **Victoria Metrics** (external monitoring) HTTP request counts. The chain: (1) register the `external.metrics.k8s.io` APIService pointing at **prometheus-adapter**, (2) get the external app's metrics into in-cluster Prometheus via an ExternalName Service + a manual Endpoints object + a ServiceMonitor with relabeling, (3) configure the adapter's `externalRules` to expose the metric (e.g. `vm_http_requests_total` → `vm_http_requests_total_external`), (4) grant the HPA controller's ClusterRole access to `external.metrics.k8s.io`, (5) HPA spec references `type: External` with the metric name and target. The HPA then scaled a StatefulSet between 2 and 4 replicas based on **actual traffic**, not CPU as a proxy.

**HPA + Cluster Autoscaler** work together: HPA scales **pods**; when new pods are Pending (no capacity), Cluster Autoscaler adds **nodes**. When HPA scales pods down and nodes are underutilized, Cluster Autoscaler drains and removes nodes. So HPA reacts to load, CA reacts to capacity."

**Common HPA failure: thrashing (scaling up/down rapidly).** Causes: (1) target too close to actual usage — add stabilization window (`behavior.scaleDown.stabilizationWindowSeconds`), (2) pods start slowly — by the time new pods are Ready the load dropped, fix startup time or tune readiness probes, (3) metric has high jitter — HPA on a smoothed/averaged metric instead of instant values.

**Trade-offs:** 
- Resource-based HPA (simple, works for most workloads) vs external-metrics HPA (scales on real demand, but complex setup).
- CPU-based (safe, compressible) vs memory-based (tricky, not compressible — use as secondary signal).
- HPA alone (scales pods, waits for capacity) vs HPA + Cluster Autoscaler (adds nodes automatically, fully elastic but slower to scale up).

**Service mesh mention (optional advanced topic):** If you're running Istio/Linkerd, HPA can scale on **service-level metrics** (request rate, error rate per service) automatically exposed by the mesh, which is cleaner than manual external-metrics setup — the mesh already instruments every service. But service mesh is overkill unless you have 50-100+ microservices with heavy east-west traffic.

**Bonus — probes for legacy/stateful workloads (real):** "For a WebLogic monolith with long startup and operator maintenance, naive liveness probes fight the operator. I used **file-flag probes** — a `configuring` file makes the probe mock success during bootstrap so I could drop a huge `initialDelaySeconds`; a `maintenance` file on a shared volume lets OPS bounce WebLogic without the pod being recreated. Not textbook 12-factor, but the right escape hatch for a legacy stateful app."

---

# PROMPT 5 — Design a rollout system for pushing a new version to thousands of tenants/orgs

**★★ This IS your Salesforce push-upgrade system. Your single strongest prompt — own it end to end.**

**Clarify:** How many tenants? Is the operation reversible? Platform rate limits? Compliance/change-management? How do you know a tenant "succeeded"?

**High-level design (the real architecture):**
- **Request/job model:** one **PushRequest** per scheduled wave fans out to one **job per tenant**, each with its own status; failures produce **error records** with message/severity. Track health at both request and job level.
- **Dry-run / eligibility check FIRST:** a read-only pre-flight that reports *how many tenants would be affected* without doing anything — validate that blast-radius count against the approved change ticket before any irreversible action. (Real: same command with `-Dsf.isEligibilityCheck=true`, grep the eligible count.)
- **Blast-radius segmentation:** split tenants by sensitivity — high-value / restricted tenants roll out in **isolated waves**, explicitly *excluded* from the general population, so a bad push can't hit your most important customers in the same wave.
- **Rate-limit-aware batching:** chunk into **priority tiers** (batch sizes 199 / 599 in my case) to match the platform's bounded push queue — classic **backpressure**: shape the producer to a constrained consumer.
- **Idempotent, self-shrinking retries:** rather than tracking which tenants succeeded, rely on the **server-side eligibility check** to naturally exclude already-upgraded tenants — so each retry pass targets only the remainder, and the loop **self-terminates when zero remain**. Safe to re-run.
- **Governance gate:** every production wave passes **change-case validation** (an approved change window) before it runs, plus input guards (strict ID/version format checks, correct-folder / not-timer-triggered checks) against accidental prod runs.
- **Real-time status:** post segregated request- and job-level updates to **Slack** on a bounded polling loop, and feed job/error data into a **dashboard** (ETL into an analytics store, upsert-on-external-ID so re-runs don't duplicate).
- **Independent validation:** a separate suite verifies the rollout with **zero time-window assumptions** — keying off version + status, not "last N hours" — and does a **two-source reconciliation** against an independent "eligible orgs" dataset (exact match for production, small variance tolerated for sandbox/inactive that churn).

**Failure:** bad version → halt remaining waves (segmentation means most tenants are untouched), fix forward with a patch, use the de-duplicated error summary to find affected tenants. Jobs are idempotent and resumable.

**Trade-offs:** batched priority waves (safe, slower) vs push-all-at-once (fast, catastrophic blast radius). Server-side eligibility for idempotency (no state to manage) vs client-side success tracking (more control, more state/complexity). Human-in-the-loop approval on high-blast-radius waves (I gate on an `input()` approval with timeout + authorized submitters) vs full automation (faster, riskier).

---

# PROMPT 6 — Design an Infrastructure-as-Code / self-service platform

**★ Your Terraform-Shepherd (OKE) + GSPANN Ansible platform.**

**High-level design:**
- **Terraform modules** (reusable, versioned) → **remote state with locking** → CI validates `plan` → approval → `apply`. Drift detection. Self-service via a portal / Terraform Cloud / Backstage.
- **Guardrails:** policy-as-code (OPA/Sentinel).

**Deep-dive — composability & multi-tenancy (real patterns):**
- **Feature-flag map (real, Terraform-Shepherd):** a `deployments.tf` locals block of booleans — `containerengine_cluster`, `bastion`, `load_balancer`, `autonomous_database` — with each resource gated `count = deployments.<x> ? 1 : 0`. One clean toggle point to compose whole environments from the same codebase — a practical alternative to per-env branches or workspaces.
- **Data-driven network rules (real):** security lists built from a data structure via **dynamic blocks**, so adding a rule is a data change, not new HCL. Subnet CIDRs from a locals mapping, not hardcoded.
- **Multi-tenancy via templating, not forks (real, GSPANN):** one Ansible codebase served **7 teams** selected by a `teamname` parameter — per-team settings via Jinja2 templates + `when` conditions, so onboarding a team was a config change, not a code fork. Same lesson applies to IaC: parameterize, don't fork.
- **Config-as-code + idempotency (real, GSPANN):** Jenkins masters were fully reproducible from `init.groovy.d` scripts; playbooks detected the installed version and no-oped if unchanged; versioned installs + a `current` symlink gave atomic upgrade and instant rollback. **Validate after provision** — read live config via xpath, diff against a per-team baseline, and run live integration smoke tests, so "did it deploy" becomes an evidence-based check.

**Trade-offs:** central control (consistency, guardrails) vs team autonomy (velocity). Module abstraction (reuse) vs flexibility (escape hatches). Feature-flag map (simple, one file) vs workspaces vs per-env branches (more isolation, more drift risk).

---

## PRACTICE METHOD

For each prompt: set a **35-minute timer**, talk through all 7 framework steps out loud, and **draw the boxes** on paper. Then self-check:
- Did I **clarify** before designing?
- Did I name at least **2–3 trade-offs** with the rejected alternative?
- Did I cover **reliability + observability + security + cost**?
- Did I anchor in a **real system** where I have one? (Prompts 1, 2, 5 — always. 3, 4, 6 — you have real material too.)

## YOUR REUSABLE "SENIOR SIGNAL" PHRASES
- "The failure mode I'm most worried about is…" (shows you design for failure first)
- "A single health signal isn't enough — the apiserver looked healthy while storage was wedged." (real, memorable)
- "This is backpressure — I shaped the producer to match a constrained consumer." (batching)
- "Fail-closed — I never propagate a secret I haven't validated." (rotation)
- "Compliance was designed into the pipeline via separation of duties, not bolted on." (CD)
- "Managed services reduce toil on undifferentiated heavy lifting." (OKE vs self-managed)

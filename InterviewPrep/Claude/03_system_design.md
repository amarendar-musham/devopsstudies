# System Design Prep (DevOps / Platform / SRE)

> At senior level you'll design an infra/platform system and defend trade-offs. They score **structured thinking**, not a perfect answer.

---

## THE FRAMEWORK (use this every time)
1. **Clarify** — requirements, scale, constraints, SLOs. Don't design blind. Ask:
   - How many users/services/requests? Growth rate?
   - Availability target (99.9? 99.99?)? Latency needs?
   - Budget / existing cloud (OCI/AWS)? Team size/skill?
   - Compliance/security constraints?
2. **Define scope** — state what you WILL and WON'T cover in the time.
3. **High-level design** — draw the boxes: sources → pipeline → compute → storage → observability.
4. **Deep-dive** — pick 1–2 components they care about, go deep.
5. **Scale & failure** — bottlenecks, single points of failure, what happens when X dies.
6. **Trade-offs** — name the alternatives you rejected and why.
7. **Wrap** — summarize, note what you'd add with more time.

## CROSS-CUTTING CONCERNS (sprinkle these — signals seniority)
- **Reliability:** redundancy, health checks, auto-healing, blast-radius control, canary/blue-green.
- **Observability:** metrics (Prometheus), dashboards (Grafana), logs (ELK), alerting, SLIs/SLOs.
- **Security:** least-privilege IAM, secrets management (Vault), network segmentation, private endpoints, image scanning.
- **Cost:** right-sizing, autoscaling, spot/preemptible, cleanup of stale resources.
- **Automation:** IaC (Terraform), GitOps, self-service.

---

## PROMPT 1 — Design a CI/CD platform for 100+ microservices
**Clarify:** how many teams, deploy frequency, mono vs multi-repo, target (K8s?), rollback needs.
**Design:**
- Source: Git (per-service repos) → webhook triggers.
- CI: Jenkins (or GitLab CI) with **Kubernetes agents** (ephemeral pods) for scale. Stages: build → unit test → **security scan (Fortify/SAST + image scan)** → publish artifact (JFrog/OCIR).
- CD: **Helm charts** per service; deploy via pipeline or GitOps (ArgoCD). **Canary/blue-green** for prod; `helm rollback` on failure.
- Environments: dev → staging → prod, promotion gated by tests + approvals.
- Observability: pipeline metrics, deploy success rate, DORA metrics.
**Trade-offs:** Jenkins (flexible, you know it) vs GitLab CI (simpler) vs ArgoCD GitOps (declarative, pull-based). Ephemeral K8s agents vs static (cost/isolation vs startup latency).
**Your edge:** this is literally your Oracle + Salesforce work — lean on it.

## PROMPT 2 — Design secrets management for an org
**Clarify:** how many services/accounts, rotation frequency, cloud, compliance.
**Design:**
- Central store: **HashiCorp Vault** (dynamic secrets + KV) and/or cloud KMS (OCI Vault).
- **Rotation pipeline** (your real story): reset → **validate new credential works** → propagate to consumers only after validation. Parallelize I/O.
- Access: short-lived tokens, least-privilege policies, audit logging.
- Distribution: apps fetch at runtime (never bake into images); K8s via CSI secrets driver / Vault agent injector.
**Failure modes:** validation gate prevents propagating broken secrets; what if Vault is down (caching, HA/Raft)?
**Trade-offs:** Vault (powerful, ops overhead) vs cloud-native KMS (simpler, lock-in).

## PROMPT 3 — Design a multi-region, highly available Kubernetes platform
**Clarify:** RTO/RPO, active-active vs active-passive, stateful workloads?
**Design:**
- Managed K8s (OKE/EKS) per region; cluster autoscaler + HPA.
- Ingress: global load balancer / DNS failover (health-checked).
- State: replicated DB (or managed multi-region DB), object storage cross-region replication.
- Networking: VCN peering / DRG, private subnets, NSGs.
- Delivery: same Helm/GitOps to all regions.
**Failure:** lose a region → traffic shifts; lose a node → pods reschedule; lose an AZ → multi-AZ node pools.
**Trade-offs:** active-active (complex, low RTO) vs active-passive (simpler, higher RTO). Data consistency vs latency.

## PROMPT 4 — Design a monitoring & alerting stack
**Design:** Prometheus (scrape metrics) → Grafana (dashboards) → Alertmanager (routing) → PagerDuty/Slack. Logs to ELK. Define **SLIs** (latency, error rate, availability) and **SLOs**; alert on **symptoms/burn rate**, not causes. Long-term metrics storage (Thanos/Cortex).
**Trade-offs:** pull (Prometheus) vs push; alert fatigue → alert on user-facing symptoms only.

## PROMPT 5 — Design a rollout system for pushing a new version to thousands of tenants/orgs
**Your Salesforce push-upgrade story, generalized.**
**Design:** request/job model → batching → **canary a small % first** → monitor success rate → proceed or halt → real-time status (Slack + dashboard) → automated retry/remediation for failed jobs.
**Failure:** bad version → halt rollout, limit blast radius, roll back canary. Idempotent, resumable jobs.

## PROMPT 6 — Design infrastructure-as-code / self-service platform
**Design:** Terraform modules (reusable, versioned) → remote state (locking) → CI validates plan → approval → apply. Drift detection. Self-service via a portal / Terraform Cloud / Backstage. Guardrails: policy-as-code (OPA/Sentinel).
**Trade-offs:** central control vs team autonomy; module abstraction vs flexibility.

---

## PRACTICE METHOD
For each prompt: set a 35-min timer, talk through all 7 framework steps out loud, draw boxes on paper. Then check: did I clarify first? did I name trade-offs? did I cover reliability + observability + security + cost?

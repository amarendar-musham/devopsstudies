# Technical Q&A — Core DevOps/SRE Knowledge

> Rapid-fire fundamentals interviewers use to probe depth. Answer out loud in 30–60s each. Answers are concise — expand where it's your strength.

---

## KUBERNETES
- **Pod vs Deployment vs ReplicaSet?** Pod = smallest unit (1+ containers). ReplicaSet = keeps N pod replicas. Deployment = manages ReplicaSets, enables rolling updates/rollback.
- **Service types?** ClusterIP (internal), NodePort (port on each node), LoadBalancer (cloud LB), ExternalName. Ingress routes L7 HTTP to services.
- **What's an Ingress?** L7 (HTTP/HTTPS) routing layer above Services. Requires Ingress Controller (Nginx/Traefik/cloud-native). Handles host/path-based routing, TLS termination. One Ingress (one LB) → many backend Services, cheaper than LB-per-service.
- **How does a rolling update work?** Deployment spins up new-version pods, waits for readiness, terminates old ones per maxSurge/maxUnavailable. Rollback = revert to previous ReplicaSet.
- **Liveness vs readiness vs startup probes?** Liveness = restart if failing. Readiness = remove from service endpoints until ready. Startup = for slow-starting apps, gates the other two.
- **Requests vs limits?** Request = guaranteed/scheduled amount. Limit = hard cap (CPU throttled, memory → OOMKill).
- **How does HPA work?** Scales pod count on observed metrics (CPU/mem/custom) vs target. Formula: `desiredReplicas = ceil(currentReplicas * currentMetric/target)`. Queries metrics-server every 15s. External metrics via prometheus-adapter. Cluster Autoscaler scales nodes when pods are Pending.
- **Canary vs blue-green?** Canary = deploy new version alongside stable, route small % traffic to it (via ingress weighted routing or replica-count ratio), ramp up gradually. Blue-green = two full envs, atomic switch (instant rollback, 2x capacity cost).
- **What's a DaemonSet / StatefulSet?** DaemonSet = one pod per node (agents/logging). StatefulSet = stable identity + storage (databases).
- **How do pods get config/secrets?** ConfigMaps (config), Secrets (sensitive, base64 — pair with Vault/CSI for real security).
- **How does networking work?** Every pod gets an IP (CNI); Services provide stable virtual IP; kube-proxy / iptables/IPVS routes; CoreDNS for service discovery.
- **A pod is CrashLoopBackOff — how do you debug?** `kubectl describe pod` (events), `kubectl logs --previous`, check probes, resources (OOM?), image/config, exec in if it stays up.

## CI/CD
- **Scripted vs declarative Jenkins pipeline?** Declarative = structured, easier, `pipeline{}` block. Scripted = full Groovy, more flexible/complex.
- **Where do you put security scanning?** SAST (Fortify) on code post-build, image scanning before publish, DAST (WebInspect) against a deployed test env. Fail the build on high/critical.
- **What's GitOps?** Git is source of truth; a controller (ArgoCD/Flux) continuously reconciles cluster to match repo. Pull-based, auditable.
- **How do you do artifact management?** Versioned artifacts in JFrog/Nexus/OCIR; immutable tags; promote same artifact across envs (don't rebuild).

## CLOUD (OCI / AWS)
- **VCN/VPC basics?** Isolated virtual network; public subnet (route to internet gateway) vs private (NAT/service gateway for egress only).
- **Gateways:** Internet GW (public in/out), NAT GW (private egress only), Service GW (private access to cloud services, no internet), DRG (connect VCNs / on-prem).
- **Security list vs NSG?** Security list = subnet-level rules. NSG = attached to specific resources (finer-grained). Prefer NSGs.
- **Load balancer health checks?** LB probes backends; unhealthy ones removed from rotation automatically.
- **How do you secure SSH to private instances?** Bastion service (time-bound, audited) — no public IPs on the workloads.
- **IAM least-privilege?** Grant only needed actions; use groups/dynamic groups; compartments for isolation; audit with logs.

## TERRAFORM / IaC
- **State file — what and why locking?** Maps config to real resources. Remote state (S3/OCI bucket) + locking (DynamoDB/native) prevents concurrent-apply corruption.
- **Module?** Reusable, parameterized package of resources. Version them.
- **plan vs apply?** Plan = preview diff. Apply = execute. Always review plan in CI before apply.
- **Drift?** Real infra diverged from state/config; detect via `plan` / drift detection; reconcile.
- **How do you structure multi-env?** Separate state per env, shared modules, workspaces or dir-per-env.

## LINUX / TROUBLESHOOTING
- **A server is slow — how do you investigate?** `top`/`htop` (CPU), `free`/`vmstat` (memory), `iostat`/`iotop` (disk), `df -h` (disk full), `netstat`/`ss` (connections), check logs (`journalctl`, `/var/log`), `dmesg` (kernel/OOM).
- **High load average but low CPU?** Likely I/O wait or blocked processes — check `iostat`, disk.
- **Out of disk — find the culprit?** `du -sh /*` drill down, `df -i` for inodes, check logs/tmp/large files.
- **A process eating memory?** `ps aux --sort=-%mem | head`, check for leaks, OOM in dmesg.
- **How do you find what's listening on a port?** `ss -tlnp` / `lsof -i :PORT`.

## NETWORKING
- **What happens when you type a URL?** DNS resolve → TCP handshake → TLS → HTTP request → response. (Be ready to go deep.)
- **DNS record types?** A (IPv4), AAAA (IPv6), CNAME (alias), MX (mail), TXT.
- **TCP vs UDP?** TCP = reliable, ordered, connection. UDP = fast, connectionless, no guarantees.
- **What's a reverse proxy / LB do?** Terminates client connections, distributes to backends, TLS termination, health checks.

## OBSERVABILITY / SRE
- **SLI vs SLO vs SLA?** SLI = measured indicator (latency, error rate). SLO = internal target. SLA = external contract w/ penalties.
- **Error budget?** 100% − SLO. Spend it on releases; freeze changes when exhausted.
- **What do you alert on?** User-facing symptoms + burn rate, not every cause. Avoid alert fatigue.
- **Metrics vs logs vs traces?** Metrics = aggregates/trends. Logs = discrete events. Traces = request path across services.
- **Prometheus pull model?** Scrapes `/metrics` endpoints on an interval; targets via service discovery.

## SECURITY
- **How do you manage secrets?** Central store (Vault/KMS), short-lived tokens, never in code/images/logs, rotation with validation, audit.
- **Least-privilege in practice?** Scoped IAM roles, no wildcard admin, separate accounts per env, review access.
- **Container image security?** Minimal base images, scan for CVEs, no root, signed images, pinned versions.

---

## RAPID-FIRE SELF-TEST
Cover the answers and explain each aloud. If you stumble, that's your study target. Prioritize Kubernetes, CI/CD, and Cloud — your interview core.

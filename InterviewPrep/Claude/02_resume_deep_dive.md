# Resume Deep-Dive — Answer Cheatsheet

> Interviewers drill your resume line by line. This file gives you **model answers** for every bullet, grounded in your real work. Read the answer, then say it in your own words — don't memorize verbatim.
>
> **Legend:**
> - ✅ **Grounded** = pulled from your actual Salesforce/Oracle/GSPANN artifacts. Defensible.
> - ⚠️ **(verify)** = a reasonable answer, but confirm the specifics match what *you* actually did before you say it in an interview.
>
> **Golden rule:** never volunteer a number you can't defend. When you don't have a metric, use honest qualitative proof ("it removed the manual step entirely", "the eligibility count matched the change case").

---

# SALESFORCE — Software Engineering, SMTS (June 2025 – Present)

---

## Bullet: Secret rotation for ~90 service accounts (Python, 1Password, Vault, multithreading) ✅

**Q: Walk me through the pipeline end to end.**
"It rotates passwords for around 90 Salesforce org service accounts and keeps our secret stores in sync, with no human ever handling a raw credential. It's a per-account workflow driven off a mapping of username → 1Password item → Vault secret. For each account it: (1) SOAP-logs in to the org with the *current* password, (2) calls the SOAP `changeOwnPassword` API to set the new one, (3) **validates by logging in again with the new password**, and (4) *only if that validation passes* propagates the new secret — first to 1Password, then to HashiCorp Vault for accounts that have a Vault mapping. It runs one account or the whole set in a single invocation, and the accounts rotate in parallel. The result is that rotation is a one-command operation instead of ~90 manual, error-prone password changes."

**Q: Why gate on login validation *before* propagating? What if you skip it?**
"Because the failure mode I'm most afraid of is propagating a broken secret. The org password is the source of truth — if I change it and then push an unconfirmed value into 1Password and Vault, every consumer of that account is now broken and I've caused an outage. So I re-authenticate with the new password first, and only a *successful* login unlocks the store updates. It's fail-closed. I also made the propagation order deliberate: org → 1Password → Vault, so the store that the widest set of automated consumers reads from is updated last, only after the credential is fully proven."

**Q: What if a step fails mid-run — how do you avoid leaving accounts broken?**
"Every account is handled independently, so one failure never blocks the others, and the run ends with a succeeded/failed summary plus a non-zero exit code so it's safe to re-run just the failures. Each partial-failure state is handled explicitly and surfaced with an actionable message — for example if the org password changed but a downstream store update fails, the tool flags exactly which account and which store need reconciliation, and the previous value in the store is still the last-known-good so consumers keep working on it until that one account is remediated. There's no silent failure."

**Q: Why 1Password *and* Vault — what goes where?**
"They serve different consumers. 1Password is the human/team store — where an engineer would go to grab a credential interactively. Vault is the machine-consumption path — our release-ops pipelines pull from the `kv/ire-managed` mount at runtime, keyed by secret name and field. Not every account is machine-consumed, so Vault is only updated for accounts that have a mapping; the rest live in 1Password only. Keeping both in sync automatically is the whole point — before, they could drift."

**Q: How do you authenticate to the stores themselves?**
"1Password is the `op` CLI with a biometric session — I verify the session once up front so the whole batch only prompts for biometrics a single time, not per account. Vault is **cert-based auth** — `vault login -method=cert` with a CA cert, client cert, and client key, against our internal Vault endpoint using a scoped read-write role. Vault auth also happens once up front, and only if at least one account in the batch actually needs a Vault update."

**Q: Why multithreading — wasn't rotation CPU-light?**
"Right — it's not CPU-bound, it's **I/O-bound**: nearly all the wall-clock time is network round-trips to Salesforce SOAP, the `op` CLI, and Vault. So I use a `ThreadPoolExecutor` to overlap those waits and rotate many accounts concurrently instead of serially. One subtlety: the *store writes* to 1Password and Vault are serialized behind a lock even though the rotations run in parallel, because concurrent writes were hitting 409 conflicts. So it's parallel where it's safe — the network-bound logins and rotations — and serialized only on the store-write section. Threads, not multiprocessing, because there's no CPU work to parallelize."

**Q: How do you keep the secrets themselves safe — nothing leaking to logs or process listings?**
"Secrets are held in memory only and travel to the stores over TLS. The new password is passed via stdin/environment rather than as a command-line argument, so it can't show up in a process listing or shell history, and nothing sensitive is echoed to logs. Access to the stores is least-privilege — a scoped Vault role and a per-user biometric-gated 1Password session — and the tool touches only the specific items it's mapped to."

**Q: Does it support a dry run?**
"Yes — a `--dry-run` flag prints exactly what it *would* do per account (login, changeOwnPassword, validate, update 1Password, update which Vault secrets) without making any changes, so I can confirm the plan and the Vault mappings before touching production credentials."

---

## Bullet: Package push upgrades across thousands of jobs per release ✅

> This is your strongest, best-documented area. Ground it in the real mechanism.

**Q: What is a PackagePushRequest vs a PackagePushJob?**
"They're the Salesforce push-upgrade data model. A **PackagePushRequest** is one scheduled push of a specific package version — it has a status and a scheduled start time. Under it are many **PackagePushJobs**, one per subscriber org, each with its own status and a SubscriberOrganizationKey. When a job fails you get **PackagePushError** rows with the message, severity, and type. So one request fans out to thousands of jobs, and I track health at both levels."

**Q: How does the push-upgrade pipeline work end to end?**
"It's a Jenkins job that takes a package name and version plus a target-org selector, and everything funnels down to one Gradle task — `executePushUpgrade` in our packaging-api project — which calls Salesforce's push-upgrade API. I check out our internal build repo into a clean workspace, assemble the Gradle `-D` parameters based on the chosen org type, run a governance/case-validation stage, execute the push, and tee the console output to a per-build file so I can grep it for eligible / succeeded / failed counts. Then a notification stage Slacks and emails the result."

**Q: How do you sequence rollouts — all at once, batched, or canary?**
"Batched and segmented, never all at once. First, I segment by **org type** — signature orgs, active, non-active, and CPR (customer-restricted) orgs — and each maps to a different set of include/exclude flags so the sensitive orgs roll out **separately** from the general population. Second, within the engine, eligible orgs are chunked into priority tiers — batch size 199 for smaller volumes, 599 for larger ones — because the platform push queue has a bounded capacity (max 200 jobs per request). It's essentially backpressure: I shape my scheduler to match a constrained consumer."

**Q: Why run a dry-run first?**
"Because pushing to production subscriber orgs is irreversible at scale. I run the exact same Gradle command with `-Dsf.isEligibilityCheck=true` first — it computes and logs how many orgs *would* be affected without pushing anything. I grep the output for the eligible-org count and confirm it matches the approved change case before I ever do the real run. That's my blast-radius check."

**Q: What's the blast radius if a bad version ships? How do you limit it?**
"Several layers. Signature and CPR orgs — our highest-value customers — are explicitly excluded from the broad active/non-active waves via exclude-org-ID lists, so a bad general push can't hit them; they get isolated runs. There's a safety rule that when the POD group ends in `_ALL` — the final full-population run — I force the retry counter to 1 so we can't accidentally re-push across everyone. And nothing runs without passing change-case validation first."

**Q: How do you detect and handle failed jobs, and avoid re-pushing to orgs that already succeeded?**
"The production job wraps the Gradle call in a bash until-loop bounded by a retry counter, with a configurable sleep — default 3 minutes — between attempts. After each attempt I grep the output for the eligible-org count. The key insight is that Salesforce's eligibility check **naturally excludes orgs already on the target version**, so on each retry only the ones that still need it come back — I don't have to track state myself. When eligible count hits zero, I exit. The retry variant also greps for `failed with status`, `succeeded`, and unique `Message:` lines to summarize and de-dupe errors."

**Q: How do you enforce that a production push is authorized?**
"A dedicated Case Validation stage calls `globalLib.run_validation` with the change-case / release-record parameters, and it fails the build if there's no approved change backing the push. The by-org-ID job goes further — org IDs must be exactly 15 chars with letters and digits and no quotes, versions must be integers, and it checks it's running from the correct Jenkins folder, wasn't timer-triggered, and the job name matches — throwing an AbortException otherwise. That's layered defense against an accidental prod push."

**Q: How are credentials handled?**
"Packaging-org creds live in the Jenkins credential store and I look them up by convention — the credential ID is `<cloudName>PackagingOrg`, like `FSCPackagingOrg` — via `withCredentials`. Passwords are masked with MaskPasswordsBuildWrapper, and in the notification code the password is passed to Python only through an env var, never as a CLI argument, so it can't leak into process listings."

**Q: What's your rollback / remediation plan for a bad push?**
"Push upgrades aren't trivially reversible — you'd push a corrected version forward rather than 'undo'. So the real defense is prevention: dry-run eligibility check, blast-radius segmentation, change-case gating, and the self-shrinking retry loop. If a version is bad, you halt the remaining waves (the segmentation means most orgs haven't been touched yet), fix forward with a patch version, and use the error-message summary to identify which orgs need attention."

---

## Bullet: Monitoring automation → Slack + dashboard ✅

**Q: How do you query status? What's the polling interval and why?**
"There are two flavors. The operational one is a polling loop that runs on a bounded time window — it sleeps a configurable number of minutes between iterations and stops at a computed end time — querying the PackagePush objects and posting segregated status to Slack. The interval is a trade-off: frequent enough that release managers see progress in near-real-time, but not so tight that I hammer the API or spam the channel. For the dashboards, a Jenkins job runs a Python extract, transforms it, and loads it into Einstein Analytics."

**Q: Request-level vs job-level — why segregate?**
"Because they answer different questions. Request-level tells you 'is this wave scheduled / in progress / done' — the operational heartbeat. Job-level tells you 'which specific orgs succeeded, failed, or are stuck, and what the error was' — that's what you need to actually remediate. A release manager watches request status; an engineer debugging a failure needs job and error detail."

**Q: What does the dashboard show and who consumes it?**
"It's built in Einstein Analytics / CRM Analytics. The data flow is: the source of truth is the PackagePush objects in the packaging org; a Jenkins pipeline runs a Python extract, then `prepareDashboardCSV.py` transforms it — joins error rows to job rows on PackagePushJobId to attach the subscriber org key, computes success and failure percentages, and stamps each row with release metadata. Then it loads the CSVs into Wave datasets using Salesforce's `datasetutils` JAR with upsert semantics. The dashboards show eligible org counts, request/job status, and post-run error analysis, and release managers use them to see push-upgrade health by cloud and pod group."

**Q: How do you avoid duplicate rows when the job re-runs?**
"The dataset loads are keyed on an external ID and use explicit Upsert / Append / Delete operations per dataset. Because it's upsert-on-external-ID, re-running for the same release/pod overwrites those rows instead of duplicating — which matters because these jobs run repeatedly across many release and pod-group combinations."

**Q: What happens if the query job itself fails?**
"The validation/monitoring pipeline catches exceptions and posts a 'danger'-colored Slack message with the error, rather than failing silently. For the notification loop specifically, a Jenkins timeout throws a FlowInterruptedException, which I catch and treat as a *normal, expected* end-of-window — so a timeout isn't a false failure, but a real error is surfaced loudly."

**Q: (Bonus) There's a validation suite too — what does it do?**
"Yes — beyond dashboards there's a pytest suite that independently *validates* a rollout. It was deliberately designed with **zero time-window assumptions** — instead of asking 'what happened in the last N hours', which is fragile because pushes get rescheduled and retried, it keys entirely off release version and push status. It resolves the exact package version ID, walks the requests and jobs, and asserts things like 'every scheduled instance has at least one Succeeded job for this version'. Then it does a two-source reconciliation: it compares the packaging-org counts against an independent GUS 'eligible orgs' analytics dataset — exact match required for Active orgs, up to 5% variance tolerated for Non-Active and Sandbox because those populations churn."

---

## Bullet: Onboarded verticals into CI/CD (Jenkins-based push upgrades) ✅

**Q: What does 'onboarding a vertical' involve concretely?**
"The platform is a Jenkins shared library — `globalLib` holds the cloud-agnostic logic (package upload, org creation, push upgrade, notifications) and each cloud has a thin cloud-specific lib — `hcLib` for Health Cloud, `fscLib` for Financial Services Cloud, plus vlocity, mulesoft, loyalty, and others — holding only what differs. Onboarding a vertical means wiring up its packaging-org credentials (by the `<Cloud>PackagingOrg` convention), adding its entry to the cloud→package map, its pod mappings, and a thin Jenkinsfile that calls the shared functions. Around 90 job Jenkinsfiles are thin wrappers over that shared library."

**Q: What was manual before, what's automated now?**
"The automation replaces hand-running Gradle push commands and hand-typing pod/org lists with parameterized jobs. Pod targeting is generated programmatically by a Python analyzer instead of being typed by hand, org include/exclude lists live in a JSON file that release managers edit as data, and governance — change-case validation — and notifications are built into the pipeline instead of being manual steps. So what used to be a multi-step, error-prone manual process is now a single parameterized Jenkins job."

**Q: Why is targeting data-driven (orglist.json, podMapper.yml) instead of code?**
"So release managers change *data*, not pipeline code. Org signatures live in `orglist.json` read via jq, and pod groups come from a `podMapper.yml` that a Python generator turns into the instance list. The stuff that rarely changes and is tightly coupled to our branch-naming convention — like deriving the major version from the release branch name — stays in Groovy. It's the right split: volatile config as data, stable business rules as code."

---

## Bullet: AI-assisted dev tools (Claude, Cursor) ✅

**Q: Give a concrete example of something you built faster with AI.**
"The secret rotation tooling — the whole workflow of SOAP login, changeOwnPassword, validation, 1Password and Vault updates, with the ThreadPoolExecutor parallelism and the lock-serialized store writes — I scaffolded and iterated that with Claude. It accelerated the boilerplate around the SOAP envelope construction, the `op` CLI subprocess handling, and the Vault cert-based auth flow, which I then reviewed, tested, and hardened. What would have taken days of looking up API docs and debugging XML parsing I had working in a few hours."

**Q: How do you verify AI-generated code before shipping?**
"I treat it like a junior engineer's PR — I read every line, run it, test edge cases, and never ship anything I don't fully understand. For the rotation tool specifically I tested the dry-run, a single-user run, a multi-user run, and the partial-failure recovery paths before I ever touched a production credential. For anything with high blast radius — production pushes, secrets — I'm especially careful."

**Q: Where do you NOT rely on it?**
"Anything involving production credentials, irreversible operations like a real push upgrade, or business/compliance logic like change-case gating — those I reason through myself. AI accelerates the boilerplate and API glue; the judgment and the safety design stay mine."

---

# ORACLE — Principal SE / Project Lead / Sr Software Developer (Aug 2019 – June 2025)

---

## Bullet: End-to-end OCI infrastructure (OKE, OCIR) ✅

**Q: Walk me through the architecture.**
"The core was `commerce-devops` — a large repo of Dockerfiles, shell-based Kubernetes orchestration, and Jenkins pipelines that build, certify, and deliver the Oracle Commerce product (a WebLogic monolith plus microservices) onto OCI. It ran on two flavors of Kubernetes: self-managed kubeadm clusters with a home-grown 3-master HA/VIP failover, and later Oracle Kubernetes Engine (OKE) provisioned via Terraform. Images went to OCIR. Monoliths deployed via native Kubernetes YAML; microservices via Helm charts."

**Q: Why OKE (managed) vs self-managed Kubernetes?**
"We started self-managed with kubeadm and ran three masters behind a virtual IP with our own failover script — but that's a lot of operational surface. Moving to OKE gave us a managed control plane with a private API endpoint plus a bastion for access, which removed a whole class of toil — we no longer maintained the control-plane HA mechanism ourselves. That's my honest 'why managed' story: managed services reduce operational burden where the undifferentiated heavy lifting isn't your value-add."

**Q: How did you provision it — Terraform / Resource Manager / manual?**
"Terraform, through Oracle's Shepherd release framework, which wraps Terraform with release phases and execution targets bound to a tenancy and region. It provisioned an enhanced OKE cluster with a private API endpoint, a node pool of VM.Standard flex shapes spread across availability domains, pod and service CIDRs, and a bastion. A pattern I liked was a `deployments.tf` **feature-flag map** — a locals block of booleans like `containerengine_cluster`, `bastion`, `load_balancer` — where each resource is gated with `count = deployments.<x> ? 1 : 0`, so we compose whole environments by toggling flags in one file."

**Q: How did the self-managed control-plane HA actually work?**
"Three masters behind a VIP. A cron-driven script — `master.sh` — ran effectively every 15 seconds on each master (four crontab entries with staggered sleeps). Each master health-checked its peers on four dimensions: ICMP ping, SSH with a 10-second timeout, the kube-apiserver `/healthz` on port 6443, and whether the `/u01` block volume was mounted and writable. If the primary failed, the next master claimed the VIP by calling the OCI CLI to reassign the private IP to its own VNIC and adding the address to its interface. And each master self-checked — if its own apiserver was down *and* the block volume wasn't writable, it self-rebooted. The block-volume check was a key addition; we'd seen cases where the apiserver looked healthy but storage was wedged."

**Q: How did you keep the delivery pipeline compliant?**
"Three Jenkins pipelines — Master, Main, Feature Branch — targeting commit-to-production-ready in under 5 hours. The pipeline runs cleanup, setup, base image build, image-build, then a **parallel** stage of certification testing and Anchore image scanning, then publishing to the preprod registry. We gated promotion on an 80% cert pass rate. For compliance we deliberately used Continuous **Delivery**, not Deployment — production upgrades need customer sign-off and OPS scheduling — and enforced separation of duties: only the Commerce Operations team could promote images to the prod registry, using a one-time registry token, which satisfied our PCI and SOC audits. Security scanning was layered — Anchore for images, Fortify SAST, WebInspect DAST."

---

## Bullet: Oracle APEX cost-analysis platform (Python/Pandas, SQL) ✅

**Q: Schema design — walk me through the tables.**
"Multiple tables: some hold raw cost data keyed by resource and time, others hold metadata like compartment/service mappings and ownership. The structure separates transactional cost rows from dimensional/metadata lookups so the dashboard queries can join them efficiently."

**Q: How do you pull OCI cost data? What API/format?**
"Via the OCI Usage/Cost API. I pull it with the OCI Python SDK, load into Pandas for transformation, then bulk-load into the Autonomous DB schema. That gives me real-time cost data without waiting for overnight CSV exports."

**Q: What transformations do you do in Pandas?**
"Parse and normalize the cost rows, join to compartment/service metadata, aggregate by the dimensions the dashboard needs — cost by service, by compartment, by time bucket — and compute deltas and trends. Then bulk-load into the schema so the APEX dashboard queries are fast."

**Q: Why APEX for the UI vs a custom web app?**
"APEX sits right on top of the Oracle Autonomous DB where the data already lives, so I got reporting, charts, and access control without standing up and maintaining a separate web stack. For an internal analytics/reporting tool, that's the low-toil choice — no additional deployment surface."

**Q: Who uses it and what decisions does it drive?**
"Leadership uses it for tenant-wide budget visibility and cost tracking. It flags anomalies and helps drive decisions around cutting down or optimizing usage — for example identifying over-provisioned resources or idle workloads that can be rightsized or decommissioned."

---

## Bullet: Stale-VM detection & cleanup (Python, Bash) ✅

**Q: How do you define 'stale' without deleting something in use?**
"A combination of signals — age past a threshold, no recent activity or usage, and **tag checks** looking for orphaned or no-parent-ID indicators. I don't trust any single signal — a VM can be old but still active, or unused temporarily but legitimate. The tag checks, especially detecting orphaned resources with no parent relationship, are the key signal that a VM was left behind from a deprovisioned environment. It's the same philosophy I used in my GSPANN work — for Puppet cert cleanup I computed 'inventory minus currently-active nodes' from a live source rather than trusting one field."

**Q: What safeguards before deletion (dry-run, approvals, tags)?**
"The tool publishes findings to a Flask application where they can be reviewed before action. It runs on a scheduled/cron basis but doesn't auto-delete — it surfaces the candidates and the criteria they matched so someone confirms the deletion is safe. That's the dry-run-by-default pattern: detection and reporting are automated, but the destructive action requires human review."

**Q: How is it scheduled?**
"Cron-driven on a regular interval. It publishes findings to the Flask app, which acts as the review/approval surface, so the detection runs automatically but deletion stays gated."

---

## Bullet: OCI networking (VCNs, subnets, route tables, DRGs, service gateways) ✅

**Q: Explain a VCN. Public vs private subnet routing.**
"A VCN is an isolated virtual network in OCI. A **public subnet** has a route to an Internet Gateway so resources can have public IPs and reach/serve the internet. A **private subnet** has no internet-gateway route — egress goes through a NAT gateway (outbound only) or a Service Gateway (to OCI services without traversing the internet). Workloads live in private subnets; only load balancers / bastions sit public."

**Q: Service gateway vs NAT gateway vs internet gateway?**
"**Internet Gateway** — bidirectional public traffic. **NAT Gateway** — private-subnet resources get outbound internet only, nothing inbound. **Service Gateway** — private access to OCI services (Object Storage, etc.) without going over the internet at all. **DRG** (Dynamic Routing Gateway) — connects VCNs to each other or to on-prem over FastConnect/VPN."

**Q: (Grounded detail) How did you author the security lists?**
"In the Terraform network module I built security lists from a data-driven structure using dynamic blocks — encoding the OKE-specific rules: load-balancer to worker nodeports 30000–32767, kube-proxy on 10256, worker-to-control-plane on 6443 and 12250, egress to the Oracle services network CIDR, and ICMP type 3 code 4 for path-MTU discovery. Subnet CIDRs came from a locals mapping rather than hardcoded values."

---

## Bullet: Load Balancers + FSS ✅

**Q: Backend health checks — how configured, what happens on failure?**
"The LB probes each backend on a configured path/port at an interval; a backend that fails the threshold is automatically pulled out of rotation so traffic only goes to healthy nodes, and it's added back when it recovers. For OKE the LB fronts the nodeport range and health-checks the ingress."

**Q: FSS mount targets/exports — how does an instance mount it?**
"File Storage Service exposes an NFS export via a mount target that has an IP in your subnet; instances mount it over NFS. In the Commerce clusters the OCI File Storage share (`/cc-fss-pipeline`) was mounted on every node and was a hard prerequisite — the setup scripts guarded on the FSS mount before proceeding, because shared state like logs and certs lived there."

---

## Kubernetes Ingress (OKE / general K8s) ✅

**Q: What's an Ingress and why not just use a Service?**
"A Service gives you L4 (TCP) load balancing — a stable ClusterIP and optionally a NodePort or cloud LoadBalancer. An **Ingress** sits on top and provides **L7 (HTTP/HTTPS) routing** — host-based and path-based rules that route traffic to different backend Services based on the request Host header or URL path, plus TLS termination. So one Ingress (backed by one cloud LB) can serve many services by routing rules, instead of one LoadBalancer per service which would be expensive and wasteful. Example: `foo.example.com/api → svc-api`, `foo.example.com/web → svc-web`, all through one Ingress."

**Q: What's an Ingress Controller?**
"The Ingress resource is just a config object — it does nothing by itself. An **Ingress Controller** is the actual running software that watches Ingress resources and implements the routing rules. Common ones: **Nginx Ingress** (most popular, stable), **Traefik** (simpler, dynamic config), cloud-native ones like OCI's native LB integration or AWS ALB Ingress. At OKE we used the OCI load-balancer integration, which provisions an OCI LB and programs its backend sets based on the Ingress spec."

**Q: How does an Ingress Controller route traffic to pods?**
"Two patterns. **NodePort-based** (most common): the Ingress Controller provisions a cloud LB that targets the K8s nodes on a NodePort (30000-32767 range); the NodePort Service load-balances across all pods in the cluster via kube-proxy iptables/IPVS. **Pod-IP-based** (advanced, e.g. AWS ALB Ingress): the controller directly registers pod IPs as LB backend targets, bypassing the NodePort hop — lower latency but requires the LB to reach pod IPs (CNI networking must be routable)."

**Q: How do you configure TLS / HTTPS on an Ingress?**
"Two pieces: (1) create a K8s **Secret** of type `kubernetes.io/tls` holding the cert and key (`tls.crt`, `tls.key`), and (2) reference it in the Ingress spec under `tls:` with the host and secretName. The Ingress Controller terminates TLS at the LB and forwards plain HTTP to the backend pods (or you can configure end-to-end TLS if the pods also serve HTTPS). For certificate management at scale use **cert-manager**, which automates issuing and renewing certs from Let's Encrypt or an internal CA and stores them as Secrets."

**Q: Multiple Ingress resources — how do they coexist?**
"By **IngressClass**. Each Ingress Controller registers an IngressClass (e.g. `nginx`, `traefik`, `oci`), and each Ingress resource specifies `ingressClassName: nginx`. So you can run multiple controllers side-by-side — internal-only traffic on one, public on another, or different teams using different controllers — and they ignore each other's Ingresses. Before IngressClass (K8s <1.18) this was done via annotations, which was messier."

**Q: How would you do host-based vs path-based routing?**
"In the Ingress spec under `rules:`
- **Host-based:** `host: api.example.com` → backend `svc-api`, `host: web.example.com` → backend `svc-web`. Different domains route to different services.
- **Path-based:** `host: example.com`, `paths: [{path: /api, backend: svc-api}, {path: /web, backend: svc-web}]`. Same domain, different URL paths route to different services.
You can combine both: `api.example.com/v1 → svc-api-v1`, `api.example.com/v2 → svc-api-v2`."

**Q: How does an Ingress enable canary deployments?**
"With annotations or weighted routing support in the controller. **Nginx Ingress** has canary annotations: mark one Ingress as the canary with `nginx.ingress.kubernetes.io/canary: "true"` and set `canary-weight: "10"` to send 10% of traffic to a different backend Service (the canary version). **Istio/Linkerd** (service mesh) use VirtualService resources with explicit `weight:` fields per destination. This lets you run two versions simultaneously and gradually shift traffic by adjusting the weight, which is the core of a canary rollout."

**Q: What happens if the Ingress Controller pod dies?**
"The cloud LB keeps probing the Ingress Controller pod(s) via health checks; if the pod is down the LB stops sending traffic to that node. If you run the Ingress Controller as a **DaemonSet** (one per node) or a Deployment with **multiple replicas**, other controller pods keep serving so there's no downtime. The controller is stateless — all config comes from the Ingress resources in the K8s API — so a new pod comes up, reads the Ingress specs, and resumes immediately."

---

## Bullet: Autonomous DB + private endpoints + NSG ✅

**Q: Why private endpoints? NSG vs security list?**
"A private endpoint puts the Autonomous DB on a private IP inside your VCN with no public internet access — connectivity is controlled by network rules. I enforced access with **NSGs** rather than security lists because an NSG attaches to specific resources for finer-grained control, whereas a security list applies to the whole subnet. NSGs let me say 'only these app resources can reach the DB' precisely."

---

## Bullet: OCI Bastion (time-bound SSH) ✅

**Q: Why Bastion over assigning public IPs?**
"Because a public IP on a workload is permanent attack surface. The OCI Bastion service creates **time-bound, audited** SSH sessions to resources in private subnets — the session expires, and there's a record of who connected. So the workloads keep no public IPs at all, and access is short-lived and traceable instead of a standing open door."

---

## Bullet: IAM policies (dynamic groups, compartments, least-privilege) ✅

**Q: Explain compartment design. What's a dynamic group?**
"**Compartments** are logical isolation boundaries — you group resources (by env or team) and write policies scoped to a compartment, so a policy grants access only within that boundary. A **dynamic group** is a group of *OCI resources* (like all instances in a compartment, matched by rules) rather than users — you use it so a compute instance or OKE node can be granted IAM permissions to call OCI services without embedding credentials. For example, letting worker nodes pull from OCIR or read a bucket via instance principals."

**Q: Multi-tenant access example from your work?**
"On the shared OKE dev cluster I didn't hand out cluster-admin. A privileged `devclustermanager` pod in a locked-down admin namespace onboarded each user with one scripted call that created a dedicated namespace, a service account, the RBAC binding, and the registry pull secret, then emitted a kubeconfig scoped to just that namespace. So every team got least-privilege, namespace-scoped access and the real admin kubeconfig never left the DevOps team."

---

## Bullet: Jenkins CI/CD (build, scan, deploy) + K8s agents ✅

**Q: Scripted vs declarative — which and why?**
"Both, by fit. Declarative for the straightforward jobs — the `pipeline{}` structure is readable and enforces stage structure. Scripted `node{}` blocks where I needed real Groovy control flow — for example the push-upgrade retry loops and dynamically generating N parallel provisioning steps. At Oracle the Master Jenkinsfile dynamically generated four parallel provisioning jobs and sharded the test suites across environments to cut wall-clock time."

**Q: How do agents run on Kubernetes and why?**
"Ephemeral pod-template agents — each build gets a fresh pod that's torn down after. Why: clean isolation between builds (no leftover state), and it scales elastically — you're not paying for idle static agents. The trade-off is pod startup latency per build, which is acceptable for the isolation and scale benefits."

**Q: Where does security scanning sit and what blocks a build?**
"Layered and shift-left. SAST (Fortify / Checkmarx) on the code, image scanning (Anchore) before publish, and DAST (WebInspect) against a deployed test env. In the Checkmarx jobs the build **fails on any new HIGH-severity finding**. At Oracle these ran in parallel with functional certification to keep the pipeline under its 5-hour SLO."

---

## Bullet: Helm charts (install/upgrade/rollback) ✅

**Q: Chart structure — values, templates, releases.**
"A chart is templates plus a `values.yaml` of defaults; you install it as a named release, overriding values per environment. In Commerce the microservices deployed via Helm charts (e.g. `ccsage`, `microservices-secrets`) while the monolith used raw YAML orchestrations, and promotion was done through parameterized Jenkins jobs."

**Q: How does `helm rollback` work?**
"Helm keeps a revision history of each release's rendered manifests. `helm rollback <release> <revision>` re-applies a prior revision's manifests, so you revert to a known-good state without hand-editing. That's the main reason to standardize on Helm — consistent, versioned, reversible deploys instead of ad-hoc kubectl."

**Q: How would you implement a canary deployment in Kubernetes?**
"Two approaches, depending on whether you control the ingress layer. **With an ingress controller** (Nginx, Istio, Linkerd): deploy the new version as a separate Deployment with its own pod labels (e.g. `version=v2`), update the Service selector to match *both* versions so both sets of pods receive traffic, then configure the ingress or service mesh to route a small percentage (5-10%) of requests to the `v2` pods via weighted routing rules. Monitor error rates and latency on the canary pods; if healthy, gradually shift traffic (20%, 50%, 100%) by updating the weights; if unhealthy, drop the canary weight to zero and delete the canary Deployment. **Without a smart ingress** (plain K8s Service): deploy the canary with a small replica count (e.g. 1 pod) alongside the stable Deployment's larger count (e.g. 9 pods), both selected by the same Service — K8s round-robins across all 10 pods so the canary naturally gets ~10% traffic. Scale the canary up and the stable down over time, watching metrics. The first approach gives you precise traffic control; the second is simpler but coarser."

**Q: How would you implement blue-green in Kubernetes?**
"Blue-green is about instant cutover with instant rollback. I run two full Deployments — `myapp-blue` and `myapp-green` — each with its own label (e.g. `version=blue` / `version=green`). The Service selector points at one color at a time, say `version=blue` in production. To deploy, I update the green Deployment with the new image, wait for all green pods to be Ready, run smoke tests against the green pods directly (via a separate test Service or port-forward), and then **atomically switch the production Service selector from `version=blue` to `version=green`**. Traffic cuts over instantly. If anything breaks, I flip the selector back to `blue` — that's the instant rollback. Once green is proven stable I can tear down blue or keep it as the next 'standby'. The trade-off: you need **2x capacity** running during the cutover window, which costs more than a rolling update but gives you zero-downtime and instant rollback."

**Q: Blue-green vs canary vs rolling update — when do you pick which?**
"**Rolling update** (the K8s default) is for most deploys — low risk, gradual, no extra capacity. **Canary** is when you want to test a risky change on real production traffic but limit the blast radius — you get observability on a small slice before committing. **Blue-green** is for changes where you want instant, atomic cutover and instant rollback — typically for high-risk deploys, database schema changes, or when downtime is unacceptable and you can afford 2x capacity briefly. At Oracle we used rolling for routine deploys, and in the Salesforce push-upgrade design I segment by org sensitivity which is conceptually a canary (signature orgs first, then broader waves) even though it's not K8s-native."

**Q: How do you measure canary health — what metrics and how do you decide to proceed or abort?**
"You need **real-time comparison** between canary and stable. I track: **error rate** (5xx responses), **latency** (p50/p95/p99), **request rate** (to confirm the canary is actually receiving traffic), and any business metrics if available (e.g. checkout success rate). I set **SLO thresholds** — for example if the canary's error rate is more than 2x the stable baseline, or p95 latency is >50% higher, I abort. Ideally this is automated via Prometheus queries and an operator like Flagger or Argo Rollouts that can auto-promote or auto-rollback based on those metrics, but you can also do it manually by watching Grafana dashboards and making the call."

---

# WHISK / GSPANN & APTROID (older roles — lighter drilling)

> Expect 1–2 questions. Keep it short, then pivot to Oracle/Salesforce depth. But you have real, rich GSPANN material if they dig.

## GSPANN — Jenkins/Nexus/Sonar platform (Kohl's Enterprise Dev Tools) ✅

**Q: How did you provision and manage Jenkins masters — was it manual?**
"No — fully Infrastructure-as-Code. Each tool had its own Git repo. For a Jenkins master, a parameterized Jenkins pipeline first ran **Terraform** to create the GCP VM, then **Ansible** to install and configure Jenkins. The Ansible roles installed JDK/Maven/Gradle/Ant and copied ~25 `init.groovy.d` scripts that configured Jenkins **as code** — LDAP auth, matrix authorization, GitHub Enterprise servers, credentials, CSRF. A master came up fully configured with zero manual clicking, which was the whole point — no config drift."

**Q: How did you handle upgrades and rollback safely?**
"Every version installed into its own directory — `jenkins.<version>` — with a `current` symlink pointing at the active one. The upgrade role read the running version first and no-oped if it already matched (idempotent). Otherwise it stopped the service, pulled the target WAR from our internal Nexus, repointed the symlink, restarted, and waited on the port. **Rollback was just repointing the symlink.** Same pattern for Nexus and SonarQube."

**Q: You wrote a Nexus cleanup script — what did it do?**
"Our release repos grew unbounded and filled disk. The script walked the storage tree, found each artifact's metadata, and kept only the newest N versions — default 2, with a hard floor of 2 so you can never wipe everything. Instead of hard-deleting it moved old versions to Nexus's trash so they're recoverable, had a **dry-run flag on by default**, and emailed a summary. I did the analogous thing for Puppet certs — comparing the CA inventory against live nodes from a Splunk export and unlinking the orphans."

**Q: How did you validate a provisioned instance was actually correct?**
"A dedicated validation harness: an Ansible role read the live Jenkins config XMLs via xpath, dumped ~30 actual settings to a file, and a `compare.py` diffed them against a per-team expected baseline. On top of that the pipeline ran live smoke tests in parallel — real Nexus download and upload, a GitHub API auth call, a Sonar scan, a Checkmarx scan — so we knew the integrations actually worked end-to-end, not just that config values looked right."

## APTROID ✅ (keep very short)
- AWS provisioning (EC2, S3, VPC, EBS, Route 53, ELB, Auto Scaling); Docker/docker-compose with a private registry for consistent monthly releases; Ansible/Chef config management; ELK for centralized logging + Nagios for monitoring.

---

# KUBERNETES DEEP-DIVE (Cross-Cutting Topics)

> These span multiple resume bullets but are heavily tested. Strong at Oracle.

---

## Horizontal Pod Autoscaler (HPA) ✅

**Q: What's HPA and how does it work?**
"HPA scales the number of pod replicas in a Deployment/StatefulSet based on observed metrics. It queries the K8s metrics API every 15 seconds (default), compares the current metric value to a target, and scales replicas up or down to meet the target. Formula: `desiredReplicas = ceil(currentReplicas * (currentMetric / targetMetric))`. It respects `minReplicas` and `maxReplicas` bounds. Common metrics: CPU utilization (% of requests), memory, or custom/external metrics."

**Q: What's the difference between CPU requests and CPU limits in the context of HPA?**
"HPA scales on CPU **utilization**, which is `actualCPU / requestedCPU * 100`. The `request` is what HPA uses as the baseline — if you set `cpu: 100m` as the request and HPA target is 50%, HPA tries to keep actual usage at 50m per pod. The `limit` doesn't factor into HPA's scaling decision; it's the hard cap enforced by the kubelet (CPU throttled, memory OOMKill). So **HPA needs accurate requests** — if requests are too low HPA scales too late; too high and it scales prematurely."

**Q: How does HPA scale on memory, and why is it tricky?**
"You can HPA on memory utilization (`averageUtilization` or `averageValue`), but it's tricky because memory isn't compressible like CPU. If a pod hits its memory limit it gets OOMKilled, not throttled, so by the time HPA sees high memory and scales up, pods may already be crashing. Memory-based HPA works better as a **proactive signal** combined with CPU, or for workloads with predictable, gradual memory growth (caches, buffers). For most workloads CPU-based HPA is safer."

**Q: You mentioned external metrics HPA in your work — how is that different from resource metrics?**
"Resource metrics (CPU/memory) come from the kubelet's metrics-server, scoped to the pods HPA is scaling. **External metrics** come from outside the cluster — like a queue depth, request rate from a load balancer, or custom app metrics in Prometheus or Victoria Metrics. HPA queries the `external.metrics.k8s.io` API (implemented by an adapter like prometheus-adapter), which translates the external metric into a value HPA can use. The power: you scale on the **real demand signal** — 'queue depth > 100 → scale workers' — instead of a proxy like CPU. In my Oracle work I drove HPA off Victoria Metrics HTTP request counts to scale a StatefulSet based on actual traffic, not just resource usage."

**Q: Walk me through setting up external-metrics HPA.**
"Four pieces: (1) Deploy **prometheus-adapter** (or another metrics adapter) and register it as the `external.metrics.k8s.io` APIService so HPA can query it. (2) Configure the adapter's `externalRules` to expose your external metric — for example turn a Prometheus query into a named external metric like `http_requests_per_second`. (3) Make sure the external metric source is reachable — if it's outside the cluster, create an **ExternalName Service** plus a manual Endpoints object, and a ServiceMonitor to scrape it into in-cluster Prometheus, with relabeling to swap the node name into the scrape address. (4) Grant the HPA controller access: edit the `system:controller:horizontal-pod-autoscaler` ClusterRole to add `external.metrics.k8s.io` resources. Then your HPA spec references `type: External` with the metric name and target value."

**Q: What's Cluster Autoscaler and how does it interact with HPA?**
"**Cluster Autoscaler** scales the number of **nodes** in the cluster; **HPA** scales the number of **pods**. They work together: HPA scales pods up when demand increases; if those new pods are Pending because there's no node capacity, Cluster Autoscaler sees the pending pods and adds nodes. When HPA scales pods down and nodes become underutilized, Cluster Autoscaler cordons and drains those nodes and removes them (respecting PodDisruptionBudgets). So HPA reacts fast to load, Cluster Autoscaler reacts to capacity constraints."

**Q: HPA is thrashing — scaling up and down rapidly. What's wrong and how do you fix it?**
"Likely causes: (1) **Target set too close to actual usage** — if target is 70% and actual bounces between 68-72%, HPA constantly adjusts. Fix: widen the target or add a stabilization window. (2) **Pods take too long to start** — HPA scales up, but by the time new pods are Ready the load dropped, so it scales down again. Fix: improve startup time (readiness probe tuning, faster image pulls, init container optimization) or increase HPA's `--horizontal-pod-autoscaler-downscale-stabilization` (default 5 minutes). (3) **Metric has high jitter** — spiky traffic. Fix: HPA on a smoothed/averaged metric (p95 over 2 minutes) instead of instant values. (4) **Too-aggressive scale-down** — set `behavior.scaleDown.stabilizationWindowSeconds` to delay scale-down decisions."

**Q: Can you run HPA and VPA (Vertical Pod Autoscaler) together?**
"Technically yes but **not recommended** on the same metric (CPU/memory). HPA changes replica count, VPA changes pod requests/limits — if both react to CPU they fight each other. Common safe pattern: HPA on CPU, VPA on memory only. Or use **VPA in recommendation mode** (it suggests but doesn't apply) and manually tune requests, then HPA scales replicas. In production most teams pick HPA for scale-out workloads and skip VPA except for batch/stateful workloads that don't scale horizontally well."

---

## Service Mesh (Bonus Knowledge — Optional) ✅

> You don't have hands-on service mesh experience, but you should know the concept for senior-level interviews at scale-focused companies. Keep answers high-level.

**Q: What's a service mesh and what problem does it solve?**
"A service mesh adds a **sidecar proxy** (usually Envoy) to every pod; all service-to-service traffic flows through the sidecars instead of directly pod-to-pod. The mesh handles cross-cutting concerns — **mTLS** (automatic encryption + identity between services), **traffic management** (retries, timeouts, circuit breaking, canary routing), **observability** (automatic distributed tracing, request metrics), and **policy enforcement** (rate limiting, access control) — all without changing application code. The problem it solves: in a large microservices architecture (100+ services) coding those concerns into every service is error-prone and inconsistent; the mesh centralizes it in the infrastructure layer."

**Q: Istio vs Linkerd — what's the difference?**
"Both are service meshes; the trade-off is power vs simplicity. **Istio** is feature-rich — supports multi-cluster, complex traffic routing (VirtualService with weights/mirrors/faults), integrates with many tools, but it's **heavy** (complex control plane, high resource overhead, steep learning curve). **Linkerd** is lightweight and simpler — focuses on mTLS, observability, and basic traffic splitting, lower overhead, easier to operate, but fewer advanced features. Pick Istio if you need the power and can staff the ops complexity; Linkerd if you want the core mesh benefits with less operational burden."

**Q: When would you actually use a service mesh vs just Ingress + K8s Services?**
"Service mesh makes sense when you have **many microservices with heavy inter-service (east-west) traffic** and need **mTLS, retries, circuit breaking, and tracing across all of them** automatically. If you only have a few services, or most traffic is north-south (external → service via Ingress), the mesh's complexity isn't worth it — use Ingress for north-south traffic management and native K8s networking. Service mesh shines at 50-100+ services where manually coding those concerns becomes unmanageable. The trade-off: adds latency (every request goes through two sidecars) and operational complexity (control plane, sidecar injection, version management)."

---

# THE UNIVERSAL FOLLOW-UPS (rehearse for every bullet)

1. **"Why that approach over the alternative?"** → Always have the rejected option ready. (e.g. threads vs multiprocessing for I/O; managed OKE vs self-managed; upsert-on-external-ID vs synthetic key.)
2. **"What was the hardest part?"** → Pick a real one: the 15→18 char Id idempotency bug; the block-volume-wedged-but-apiserver-healthy HA edge case; native-memory OOM above JVM heap.
3. **"What would you do differently now?"** → e.g. move older bash-script credentials to proper secret bindings; consolidate the two Salesforce persistence clients; add retry/backoff around bulk polling loops.
4. **"How did you measure success?"** → Honest, non-numeric proof: "the manual credential-handling step was gone", "the dry-run eligible count matched the change case", "HA failure edge cases dropped to near-zero after the patch."
5. **"What broke / what went wrong?"** → The CCAdmin OOM incident; the duplicate audit rows from the Id-length mismatch; a wedged block volume that looked healthy.

---

## TWO SIGNATURE "HARD PROBLEM" STORIES (memorize these — they show senior depth)

**The 15→18 character Id idempotency bug (Salesforce):**
"We had two writers for the same audit object — a Java 'Start' path and a Python 'End' path. The Java side got the job Id from a SOAP SaveResult, which returns a **15-char case-sensitive** Id; the Python side read the same Id from REST, which returns the **18-char case-insensitive** form. Both upserted on that Id as an external key, so the length mismatch created *two* rows — a Start row and an End row — instead of one. I added an `id15to18()` normalization on the Java side so both writers converge on the same case-stable 18-char record. It's an idempotency-through-stable-keys fix — and I deliberately refused a synthetic composite key because that had a known case-collision risk."

**The CCAdmin native-memory OOM (Oracle):**
"Several customers were seeing intermittent CCAdmin downtime. CCAdmin ran as a StatefulSet with a 29GB JVM heap inside a 32GB pod memory limit. Under heavy theme compilation the **non-Java native memory** — G1GC structures, code cache, thread stacks — pushed the container past 32GB, so Kubernetes OOM-killed and restarted it. I confirmed it from Grafana panels correlating restarts with native-memory spikes. Immediate fix: raise the pod limit to 45Gi while keeping heap at 29GB, giving native memory headroom; the deeper theme-compilation reduction was folded into a later release. The lesson: container limits must budget for JVM **off-heap** memory, not just `-Xmx`."

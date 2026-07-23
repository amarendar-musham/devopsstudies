# Resume Deep-Dive Prep

> Interviewers WILL drill your resume line by line. For each bullet: know the *what*, the *why you chose that approach*, the *trade-offs*, and *what you'd do differently*. Below are the likely follow-ups. Fill in / rehearse answers out loud.

---

## SALESFORCE — Software Engineering, SMTS (June 2025 – Present)

### Bullet: Secret rotation for ~90 service accounts (Python, 1Password, Vault, multithreading)
Likely questions:
- Walk me through the pipeline end to end.
- Why gate on a post-change login validation *before* propagating? What happens if you skip it?
- What if the login validation fails mid-run — how do you avoid leaving accounts broken?
- Why 1Password *and* HashiCorp Vault? What goes where?
- Why multithreading? Wasn't rotation CPU-light? (Answer: I/O-bound API calls — network waits, not CPU.)
- How do you store/retrieve the secrets securely? Any secret ever written to disk/logs?
- How often does this run? Manual trigger or scheduled?
- How do you handle rate limits / API throttling from Salesforce?
- Rollback story: a rotation partially applied — what's your recovery?

### Bullet: Push upgrades across thousands of jobs per release
Likely questions:
- What is a PackagePushRequest vs a PackagePushJob?
- How do you sequence rollouts — all at once, batched, canary?
- What's the blast radius if a bad version ships? How do you limit it?
- How do you detect and handle failed jobs?
- What's your rollback / remediation plan for a bad push?

### Bullet: Monitoring automation → Slack + dashboard
Likely questions:
- How do you query the status? Polling interval? Why that interval?
- Request-level vs job-level — why segregate?
- What does the dashboard show, and who consumes it?
- How is it scheduled (cron, Salesforce scheduler, external)?
- What happens if the query job itself fails?

### Bullet: Onboarded verticals into CI/CD (Jenkins-based push upgrades)
Likely questions:
- What does "onboarding a vertical" involve concretely?
- What was manual before, what's automated now?

### Bullet: AI-assisted dev tools (Claude, Cursor)
Likely questions:
- Give a concrete example of something you built faster with AI.
- How do you verify AI-generated code before shipping?
- Where do you NOT rely on it?

---

## ORACLE — Principal SE / Project Lead / Sr Software Developer (Aug 2019 – June 2025)

### Bullet: End-to-end OCI infrastructure (OKE, OCIR)
Likely questions:
- Walk me through the architecture. Draw it.
- Why OKE (managed) vs self-managed Kubernetes?
- How did you provision it — Terraform / Resource Manager / manual?
- How did this reduce manual setup — what was the before/after?

### Bullet: Oracle APEX cost-analysis platform (Python/Pandas, SQL)
Likely questions:
- Schema design — walk me through the tables.
- How do you pull OCI cost data? What API/format?
- What transformations do you do in Pandas?
- Why APEX for the UI vs a custom web app?
- Who uses it and what decisions does it drive?

### Bullet: Stale-VM detection & cleanup (Python, Bash)
Likely questions:
- How do you define "stale" without deleting something in use?
- What safeguards before deletion (dry-run, approvals, tags)?
- How is it scheduled?

### Bullet: OCI networking (VCNs, subnets, route tables, DRGs, service gateways)
Likely questions:
- Explain a VCN. Public vs private subnet routing.
- What's a DRG and when do you use it?
- Service gateway vs NAT gateway vs internet gateway — differences?

### Bullet: Load Balancers + FSS
Likely questions:
- Backend health checks — how configured, what happens on failure?
- FSS mount targets/exports — how does an instance mount it?

### Bullet: Autonomous DB + private endpoints + NSG
Likely questions:
- Why private endpoints? NSG vs security list?

### Bullet: OCI Bastion (time-bound SSH)
Likely questions:
- Why Bastion over assigning public IPs? Security reasoning.

### Bullet: IAM policies (dynamic groups, compartments, least-privilege)
Likely questions:
- Explain compartment design. What's a dynamic group and when used?
- Give an example least-privilege policy you wrote.

### Bullet: Jenkins CI/CD (build, scan, deploy) + K8s agents
Likely questions:
- Scripted vs declarative pipeline — which and why?
- How do agents run on Kubernetes (pod templates)? Why?
- Where does security scanning (Fortify/WebInspect) sit and what blocks a build?

### Bullet: Helm charts (install/upgrade/rollback)
Likely questions:
- Chart structure — values, templates, releases.
- How does `helm rollback` work under the hood?

---

## WHISK / APTROID (older roles — lighter drilling, but be ready)
- Jenkins hardening/backups; Nexus/JFrog artifact flow; gcloud/gsutil metrics.
- AWS provisioning (EC2/S3/VPC/ELB/Auto Scaling); Docker/docker-compose; Ansible/Chef; ELK + Nagios.
- Expect only 1–2 questions here; keep answers short and pivot to depth at Oracle/Salesforce.

---

## THE UNIVERSAL FOLLOW-UPS (prepare for every bullet)
1. "Why did you choose that approach over the alternative?"
2. "What was the hardest part?"
3. "What would you do differently now?"
4. "How did you measure success?" (use honest, non-numeric proof if you don't have a metric)
5. "What broke / what went wrong?"

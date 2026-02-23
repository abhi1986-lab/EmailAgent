# Installation & Deployment Dossier

## 1) Local Development Installation

### Prerequisites
- Python 3.10+
- `pip`

### Steps

```bash
git clone <your-repo-url>
cd EmailAgent
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

### Run CLI

```bash
PYTHONPATH=src python -m email_agent.cli
```

### Run tests

```bash
pytest -q
```

---

## 2) Docker Deployment

### Example Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md /app/
COPY src /app/src
COPY docs /app/docs
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -e .
CMD ["python", "-m", "email_agent.cli"]
```

### Build & run

```bash
docker build -t email-agent:latest .
docker run --rm -it email-agent:latest
```

---

## 3) API/Service Deployment Pattern (Recommended)

For production, keep the orchestration core and wrap it in a web service:

- FastAPI/Flask endpoint receives request payload.
- Adapter maps request into `EmailRequest`.
- `EmailOrchestrationAgent` resolves missing details (or uses pre-collected data from UI).
- `EmailScheduler` adapter targets Celery, Cloud Tasks, or managed queue.
- `EmailSender` adapter targets SES/SendGrid/SMTP.

### Suggested environment variables

- `CONTACT_STORE_BACKEND=json|postgres|crm`
- `CONTACT_STORE_PATH=contacts.json`
- `EMAIL_PROVIDER=sendgrid|ses|smtp`
- `DEFAULT_TIMEZONE=UTC`
- `NOTIFIER_BACKEND=webhook|slack|internal`

---

## 4) Cloud Deployment (generic)

### Container platform
- Build OCI image.
- Push to registry.
- Deploy to ECS, Cloud Run, AKS, or Kubernetes.

### Operational recommendations
- Mount persistent volume or migrate to managed DB for contact storage.
- Add centralized logging and alerting.
- Protect endpoints with auth and rate limits.
- Encrypt secrets in cloud secret manager.

---

## 5) Multi-environment rollout

### Dev
- JSON contact store.
- Mock sender/notifier.

### Staging
- Real email sandbox (provider test account).
- Non-production notifier channel.

### Production
- Managed DB for contacts.
- Durable scheduler.
- Real notifier integration.
- Audit logs and monitoring dashboards.

---

## 6) GitHub Codespaces Startup

This repo includes a first-class Codespaces bootstrap:

- `.devcontainer/devcontainer.json` defines the container and startup hooks.
- `scripts/codespaces-startup.sh` performs setup:
  - Creates `.venv` (if missing)
  - Installs package with `pip install -e .`
  - Generates `.codespaces/agent-env` with runtime exports

After opening the Codespace terminal:

```bash
source .venv/bin/activate
source .codespaces/agent-env
pytest -q
```

If you need to re-run setup manually:

```bash
bash scripts/codespaces-startup.sh
```

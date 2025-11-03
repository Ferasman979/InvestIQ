# InvestIQ Action Plan

## Overview

This action plan outlines the development roadmap for InvestIQ, a multi-agent banking system for the DevOps for GenAI Hackathon (Toronto 2025). The plan is organized by priority and dependencies to ensure efficient execution.

## Current State Assessment

### ✅ Completed

- Basic FastAPI backend structure
- Transaction CRUD operations (create, get, approve)
- Database models (Transaction, TransactionLedger)
- SQLite database setup
- Comprehensive documentation (ARCHITECTURE.md, CONTEXT.md, AGENTS.md, SETUP.md, DEPLOYMENT.md)

### 🔄 In Progress / Pending

- Agent implementations (Payment, Security, Credit)
- Redis queue integration
- Gemini API integration
- Notification system (Email and In-app notifications)
- Docker containerization
- Kubernetes deployment
- CI/CD pipeline
- Monitoring and observability

## Action Plan Breakdown

### Phase 1: Core Infrastructure Setup (Priority: HIGH)

**Estimated Time: 4-6 hours**

#### 1.1 Redis Queue Integration

- [ ] Install Redis client library (redis-py or rq)
- [ ] Create Redis connection utility
- [ ] Setup queue management module
- [ ] Add Redis configuration to environment variables
- [ ] Test queue operations (enqueue, dequeue, health check)

**Dependencies:** Redis instance (local or Docker)
**Files to Create:**

- `backend/utils/redis_client.py`
- `backend/utils/queue_manager.py`
- Update `.env.example` with Redis configuration

#### 1.2 Environment Configuration

- [ ] Create comprehensive `.env.example` file
- [ ] Add Gemini API key configuration
- [ ] Add Email (SMTP) credentials configuration
- [ ] Add Redis connection string
- [ ] Add database URL configuration
- [ ] Setup environment validation

**Files to Update:**

- `backend/.env.example`
- `backend/config.py` (new file for config management)

#### 1.3 Dependency Management

- [ ] Add required packages to `pyproject.toml`:
  - `redis` or `rq` (queue management)
  - `google-generativeai` (Gemini API)
  - `aiosmtplib` or `smtplib` (Email notifications)
  - `prometheus-client` (metrics)
  - `psycopg2-binary` (PostgreSQL support)
- [ ] Update Poetry lock file
- [ ] Verify all dependencies resolve correctly

**Files to Update:**

- `backend/pyproject.toml`

---

### Phase 2: Agent Development (Priority: HIGH)

**Estimated Time: 12-16 hours**

#### 2.1 Payment Automation Agent

- [ ] Create agent directory structure: `agents/payment_agent/`
- [ ] Implement agent main loop (queue subscription)
- [ ] Build recurring payment detection logic
- [ ] Integrate Gemini API for payment pattern analysis
- [ ] Implement payment execution workflow
- [ ] Add balance checking logic
- [ ] Create notification triggers
- [ ] Add error handling and retry logic
- [ ] Write unit tests

**Dependencies:** Phase 1.1, Phase 1.2
**Files to Create:**

- `agents/payment_agent/agent.py`
- `agents/payment_agent/payment_detector.py`
- `agents/payment_agent/payment_executor.py`
- `agents/payment_agent/__init__.py`
- `agents/payment_agent/tests/test_payment_agent.py`

#### 2.2 Security Verification Agent

- [ ] Create agent directory structure: `agents/security_agent/`
- [ ] Implement agent main loop (queue subscription)
- [ ] Build fraud detection logic
- [ ] Integrate Gemini API for transaction analysis
- [ ] Implement user verification workflow
- [ ] Add transaction blocking mechanism
- [ ] Create email alert system
- [ ] Add pattern learning capabilities
- [ ] Write unit tests

**Dependencies:** Phase 1.1, Phase 1.2
**Files to Create:**

- `agents/security_agent/agent.py`
- `agents/security_agent/fraud_detector.py`
- `agents/security_agent/gemini_analyzer.py`
- `agents/security_agent/verification_workflow.py`
- `agents/security_agent/__init__.py`
- `agents/security_agent/tests/test_security_agent.py`

#### 2.3 Credit Optimization Agent

- [ ] Create agent directory structure: `agents/credit_agent/`
- [ ] Implement agent main loop (queue subscription)
- [ ] Build credit score monitoring
- [ ] Implement credit utilization calculation
- [ ] Integrate Gemini API for optimization recommendations
- [ ] Build credit limit increase request logic
- [ ] Add eligibility checking
- [ ] Create notification system for credit updates
- [ ] Write unit tests

**Dependencies:** Phase 1.1, Phase 1.2
**Files to Create:**

- `agents/credit_agent/agent.py`
- `agents/credit_agent/credit_monitor.py`
- `agents/credit_agent/utilization_calculator.py`
- `agents/credit_agent/limit_optimizer.py`
- `agents/credit_agent/__init__.py`
- `agents/credit_agent/tests/test_credit_agent.py`

#### 2.4 Shared Agent Utilities

- [ ] Create common agent base class
- [ ] Implement shared Gemini client wrapper
- [ ] Create notification service abstraction
- [ ] Build logging utilities
- [ ] Add metrics collection helpers

**Files to Create:**

- `agents/base_agent.py`
- `agents/utils/gemini_client.py`
- `agents/utils/notifier.py`
- `agents/utils/logger.py`
- `agents/utils/metrics.py`

---

### Phase 3: Backend Integration (Priority: HIGH)

**Estimated Time: 6-8 hours**

#### 3.1 Queue Integration with FastAPI

- [ ] Create task enqueueing utilities in backend
- [ ] Update transaction router to enqueue agent tasks
- [ ] Add agent task routing logic
- [ ] Create task status tracking endpoints
- [ ] Implement webhook/status callback mechanism

**Dependencies:** Phase 1.1, Phase 2 (agents)
**Files to Create/Update:**

- `backend/utils/task_router.py`
- `backend/routers/agent_router.py` (new)
- Update `backend/routers/transaction_router.py`

#### 3.2 Agent Status Endpoints

- [ ] Create agent status API endpoints
- [ ] Add agent health check endpoints
- [ ] Implement task queue depth monitoring
- [ ] Create agent metrics endpoints

**Dependencies:** Phase 2
**Files to Create:**

- `backend/routers/agent_router.py`

---

### Phase 4: Database Enhancement (Priority: MEDIUM)

**Estimated Time: 4-6 hours**

#### 4.1 Agent Execution Logs

- [ ] Create agent_execution_logs table
- [ ] Add logging for all agent actions
- [ ] Implement audit trail functionality

**Files to Create:**

- `backend/models/agent_log.py`
- `backend/migrations/xxx_add_agent_logs.py`

#### 4.2 Notification Tracking

- [ ] Create notifications table
- [ ] Track notification delivery status
- [ ] Add notification history queries

**Files to Create:**

- `backend/models/notification.py`
- `backend/migrations/xxx_add_notifications.py`

#### 4.3 Credit Monitoring Tables

- [ ] Create credit_score_history table
- [ ] Create credit_utilization_tracking table
- [ ] Add credit limit increase request tracking

**Files to Create:**

- `backend/models/credit.py`
- `backend/migrations/xxx_add_credit_tables.py`

---

### Phase 5: Notification System (Priority: MEDIUM)

**Estimated Time: 4-6 hours**

#### 5.1 Email Notification Integration

- [ ] Create SMTP email client wrapper
- [ ] Implement email sending functionality (via SMTP)
- [ ] Add notification templates
- [ ] Create notification service
- [ ] Add delivery status tracking
- [ ] Handle email failures gracefully
- [ ] Setup in-app notification system (via API/WebSocket)

**Dependencies:** Phase 1.2
**Files to Create:**

- `backend/providers/email_client.py`
- `backend/services/notification_service.py`
- `backend/routers/notifications_router.py` (for in-app notifications)

#### 5.2 Notification Templates

- [ ] Create payment execution notifications
- [ ] Create fraud alert notifications
- [ ] Create credit optimization notifications
- [ ] Create balance warning notifications

**Files to Create:**

- `backend/templates/notifications.py`

---

### Phase 6: Docker Containerization (Priority: HIGH)

**Estimated Time: 6-8 hours**

#### 6.1 Dockerfiles

- [ ] Create backend Dockerfile
- [ ] Create payment agent Dockerfile
- [ ] Create security agent Dockerfile
- [ ] Create credit agent Dockerfile
- [ ] Optimize Docker images (multi-stage builds)
- [ ] Add health checks to Dockerfiles

**Dependencies:** Phase 2 (agents)
**Files to Create:**

- `infra/docker/backend.Dockerfile`
- `infra/docker/payment-agent.Dockerfile`
- `infra/docker/security-agent.Dockerfile`
- `infra/docker/credit-agent.Dockerfile`

#### 6.2 Docker Compose

- [ ] Create docker-compose.yml for local development
- [ ] Add PostgreSQL service
- [ ] Add Redis service
- [ ] Configure service networking
- [ ] Add volume mounts for development
- [ ] Create docker-compose.test.yml for testing

**Files to Create:**

- `docker-compose.yml`
- `docker-compose.test.yml`

#### 6.3 .dockerignore Files

- [ ] Create .dockerignore for backend
- [ ] Create .dockerignore for each agent

**Files to Create:**

- `.dockerignore`
- `agents/**/.dockerignore`

---

### Phase 7: Kubernetes Deployment (Priority: HIGH)

**Estimated Time: 8-10 hours**

#### 7.1 Kubernetes Manifests

- [ ] Create namespace manifest
- [ ] Create ConfigMap for environment variables
- [ ] Create Secrets manifest (template)
- [ ] Create backend deployment
- [ ] Create payment agent deployment
- [ ] Create security agent deployment
- [ ] Create credit agent deployment
- [ ] Create services for all components
- [ ] Create ingress configuration
- [ ] Add HorizontalPodAutoscaler (HPA)

**Dependencies:** Phase 6
**Files to Create:**

- `infra/kubernetes/namespace.yaml`
- `infra/kubernetes/configmap.yaml`
- `infra/kubernetes/secrets.yaml` (template)
- `infra/kubernetes/backend-deployment.yaml`
- `infra/kubernetes/payment-agent-deployment.yaml`
- `infra/kubernetes/security-agent-deployment.yaml`
- `infra/kubernetes/credit-agent-deployment.yaml`
- `infra/kubernetes/services.yaml`
- `infra/kubernetes/ingress.yaml`
- `infra/kubernetes/hpa.yaml`

#### 7.2 Kubernetes Configuration

- [ ] Setup resource limits and requests
- [ ] Configure liveness and readiness probes
- [ ] Add pod disruption budgets
- [ ] Create service accounts and RBAC

**Files to Update/Create:**

- Update all deployment manifests
- `infra/kubernetes/rbac.yaml`

---

### Phase 8: CI/CD Pipeline (Priority: HIGH)

**Estimated Time: 4-6 hours**

#### 8.1 GitHub Actions Workflow

- [ ] Create main CI/CD workflow
- [ ] Add build step (run tests)
- [ ] Add Docker image build step
- [ ] Add Docker Hub push step
- [ ] Add EKS deployment step
- [ ] Add health check verification
- [ ] Add rollback mechanism
- [ ] Configure secrets in GitHub

**Dependencies:** Phase 6, Phase 7
**Files to Create:**

- `.github/workflows/deploy.yml`
- `.github/workflows/test.yml` (optional)

#### 8.2 CI/CD Configuration

- [ ] Setup Docker Hub credentials
- [ ] Configure AWS credentials
- [ ] Add EKS cluster connection
- [ ] Setup deployment triggers (branches/tags)

**Files to Update:**

- `.github/workflows/deploy.yml`

---

### Phase 9: Monitoring & Observability (Priority: MEDIUM)

**Estimated Time: 6-8 hours**

#### 9.1 Prometheus Metrics

- [ ] Add Prometheus client to backend
- [ ] Add metrics to each agent
- [ ] Expose metrics endpoints
- [ ] Create Prometheus configuration
- [ ] Deploy Prometheus to Kubernetes

**Files to Create:**

- `backend/utils/metrics.py` (update)
- `monitoring/prometheus-config.yaml`
- `monitoring/prometheus-deployment.yaml`

#### 9.2 Grafana Dashboards

- [ ] Create Grafana deployment manifest
- [ ] Design system health dashboard
- [ ] Create agent performance dashboard
- [ ] Create business metrics dashboard
- [ ] Export dashboard JSON files

**Files to Create:**

- `monitoring/grafana-deployment.yaml`
- `monitoring/dashboards/system-health.json`
- `monitoring/dashboards/agent-performance.json`
- `monitoring/dashboards/business-metrics.json`

#### 9.3 Logging

- [ ] Setup structured logging
- [ ] Configure log aggregation
- [ ] Add log levels configuration
- [ ] Create logging utilities

**Files to Create/Update:**

- `backend/utils/logger.py` (update)
- Configure log forwarding to CloudWatch or ELK

---

### Phase 10: Testing & Documentation (Priority: MEDIUM)

**Estimated Time: 6-8 hours**

#### 10.1 Unit Testing

- [ ] Write unit tests for all agents
- [ ] Write unit tests for backend utilities
- [ ] Add test coverage reporting
- [ ] Setup pytest configuration

**Files to Create:**

- `backend/tests/`
- `agents/**/tests/`
- `pytest.ini`

#### 10.2 Integration Testing

- [ ] Create integration test suite
- [ ] Test agent queue integration
- [ ] Test end-to-end workflows
- [ ] Test error scenarios

**Files to Create:**

- `tests/integration/`
- `docker-compose.test.yml` (update)

#### 10.3 Documentation Updates

- [ ] Update README with setup instructions
- [ ] Add API documentation
- [ ] Create agent deployment guide
- [ ] Add troubleshooting section
- [ ] Update architecture diagrams if needed

**Files to Update:**

- `README.md`
- `docs/SETUP.md` (if needed)
- `docs/DEPLOYMENT.md` (if needed)

---

## Implementation Priorities

### Critical Path (Must Complete)

1. **Phase 1**: Infrastructure Setup
2. **Phase 2**: Agent Development
3. **Phase 3**: Backend Integration
4. **Phase 6**: Docker Containerization
5. **Phase 7**: Kubernetes Deployment
6. **Phase 8**: CI/CD Pipeline

### Important (Should Complete)

7. **Phase 4**: Database Enhancement
8. **Phase 5**: Notification System
9. **Phase 9**: Monitoring & Observability

### Nice to Have (If Time Permits)

10. **Phase 10**: Comprehensive Testing & Documentation Updates

## Estimated Timeline

- **Phase 1-3** (Core Development): 22-30 hours
- **Phase 4-5** (Enhancements): 8-12 hours
- **Phase 6-8** (DevOps): 18-24 hours
- **Phase 9-10** (Polish): 12-16 hours

**Total Estimated Time: 60-82 hours**

## Dependencies Map

```
Phase 1 (Infrastructure)
    ↓
Phase 2 (Agents) ──┐
    ↓              │
Phase 3 (Integration) ─→ Phase 6 (Docker)
    ↓                    ↓
Phase 4 (Database)       Phase 7 (Kubernetes)
    ↓                    ↓
Phase 5 (Notifications)  Phase 8 (CI/CD)
                            ↓
                        Phase 9 (Monitoring)
                            ↓
                        Phase 10 (Testing)
```

## Risk Mitigation

### Technical Risks

- **Redis/Queue Issues**: Have fallback to direct API calls
- **Gemini API Rate Limits**: Implement rate limiting and retry logic
- **Docker Build Failures**: Test locally before CI/CD
- **Kubernetes Deployment Issues**: Test with minikube/kind first

### Time Risks

- **Agent Complexity**: Start with MVP versions, iterate
- **Kubernetes Learning Curve**: Use provided templates and examples
- **CI/CD Configuration**: Setup basic pipeline first, enhance later

## Next Steps

1. Review and approve this action plan
2. Prioritize phases based on hackathon timeline
3. Assign team members to specific phases
4. Setup development environment
5. Begin Phase 1: Infrastructure Setup

## Notes

- Each phase should be tested independently before moving to the next
- Keep documentation updated as development progresses
- Regular code reviews and team syncs recommended
- Demo preparation should start early (working prototype)

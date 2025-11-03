# Project Context

🧠 Cursor Project Context: DevOps for Gen AI Hackathon

## 🎯 Project Overview

**Name**: InvestIQ - AI-Powered Autonomous Banking Assistant

**Hackathon Track**: Track 3 — Agent Deployment at Scale (DevOps for GenAI Hackathon, Toronto 2025)

### Summary

A multi-agent banking system leveraging AI to automate key financial workflows:

- **Detect and execute recurring payments**
- **Verify and block fraudulent transactions**
- **Optimize credit utilization and limit increases**
- **Notify users proactively through email and in-app notifications**

Each agent is an independent microservice using **Google Gemini API** for reasoning, orchestrated through a DevOps-enabled system that scales autonomously on **Kubernetes (EKS)**.

## ⚙️ System Design Context

### Core Agents

| Agent                           | Responsibility                                                                             |
| ------------------------------- | ------------------------------------------------------------------------------------------ |
| **Payment Automation Agent**    | Identifies recurring payments, executes them automatically, alerts if balance insufficient |
| **Security Verification Agent** | Detects suspicious transactions and interacts with user for verification/approval          |
| **Credit Optimization Agent**   | Monitors credit score/utilization and submits increase requests if user eligible           |

### Shared Components

- **Task Router**: Redis Queue or RabbitMQ for message passing
- **Database**: PostgreSQL (or SQLite for demo)
- **LLM Engine**: Google Gemini API for reasoning and conversations
- **Notification System**: Email (SMTP) and In-App notifications via Streamlit UI for transparency

## 🏗️ Architecture Flow

```
User → Frontend/UI (Streamlit)
       ↓
Backend API (FastAPI)
       ↓
Redis Queue (Task Routing)
       ↓
─────────────────────────────
| Payment Agent  |  Security Agent  |  Credit Agent |
─────────────────────────────
       ↓
PostgreSQL (State + Logs)
       ↓
Notifications (Email & In-App)
```

**Kubernetes (EKS)** manages containers for all agents. **GitHub Actions** automates build → test → push → deploy.

## 🧩 DevOps Setup Plan

### Infrastructure

- **Cloud**: AWS (EKS + RDS free-tier, $100 credit budget)
- **Orchestration**: Kubernetes (EKS, 2×t3.small nodes)
- **IaC**: Terraform or AWS CLI
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Containerization**: Docker + DockerHub Registry

### Development Environment

- **Language**: Python 3.11+
- **Frameworks**: FastAPI, LangChain (optional), Celery/RQ
- **Frontend (optional)**: Streamlit or Next.js
- **APIs**: Gemini API (fraud/credit reasoning)
- **Logging**: ELK or local file-based logging

## 🧪 Execution Roadmap

1. ✅ **Setup environment** – Python, Redis, Gemini key, local Docker
2. 🔄 **Build Payment Agent** – recurring payment logic + notifications
3. 🔄 **Build Security Agent** – fraud detection workflow + LLM interaction
4. 🔄 **Build Credit Agent** – credit monitoring and increase automation
5. 🔄 **Integrate all agents** – queue-based orchestration
6. 🔄 **Deploy on EKS** – automate with GitHub Actions
7. 🔄 **Add observability** – metrics dashboards in Grafana
8. 🔄 **Prepare demo** – working multi-agent app + pitch deck

## 🧮 Judging Rubric Focus

| Criterion               | Implementation Focus                               |
| ----------------------- | -------------------------------------------------- |
| **Innovation (25%)**    | Multi-agent self-acting system in banking domain   |
| **Complexity (20%)**    | Containerized microservices, EKS orchestration     |
| **CI/CD (15%)**         | GitHub Actions automation for build/deploy         |
| **Usability (10%)**     | Simple UI + Email/In-app notification transparency |
| **AI Tool Usage (10%)** | Gemini LLM for fraud reasoning and credit logic    |
| **Collaboration (10%)** | Modular agent development + version control        |

## 🧰 Suggested Folder Layout

```
investIQ/
├── agents/
│   ├── payment_agent/
│   ├── security_agent/
│   └── credit_agent/
├── backend/
│   ├── app.py              # FastAPI backend
│   ├── routers/            # API route handlers
│   ├── schemas/            # Pydantic models
│   ├── providers/          # External service providers
│   └── db/                 # Database models and connections
├── frontend/               # Streamlit or Next.js UI
├── infra/
│   ├── docker/
│   │   ├── Dockerfile
│   └── kubernetes/
│       ├── deployment.yaml
│       ├── service.yaml
├── ci-cd/
│   └── github-actions.yaml
├── monitoring/
│   ├── prometheus-config.yaml
│   └── grafana-dashboard.json
├── data/
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md
│   ├── SETUP.md
│   └── CONTEXT.md
├── .env.example
└── README.md
```

## 🧭 Cursor Usage Guidelines

When generating content inside Cursor:

### Docs Mode

> "Generate a project README and architecture overview based on CONTEXT.md"

### DevOps Mode

> "Generate EKS deployment YAML for 3 microservices defined in CONTEXT.md"

### Diagram Mode

> "Create Mermaid system diagram showing multi-agent banking flow"

### Prompting Mode

> "Suggest CI/CD workflow YAML compatible with GitHub Actions and DockerHub"

Cursor should automatically reference this file to provide consistent, DevOps-grade documentation and code.

## 🔑 Key Design Decisions

### Why Multi-Agent Architecture?

- **Separation of Concerns**: Each agent has a focused responsibility
- **Independent Scaling**: Agents scale based on their own workload
- **Fault Isolation**: Failure in one agent doesn't affect others
- **Parallel Processing**: Multiple agents can work simultaneously

### Why Gemini API?

- **Reasoning Capabilities**: Strong at financial decision-making
- **Cost-Effective**: Efficient pricing for high-volume operations
- **Integration**: Easy API integration with Python

### Why Kubernetes?

- **Scalability**: Auto-scaling based on queue depth
- **Reliability**: Health checks and auto-restart
- **Portability**: Runs on any cloud provider
- **Industry Standard**: Widely used in production environments

### Why Message Queue?

- **Decoupling**: API and agents are independent
- **Reliability**: Tasks persist even if agents restart
- **Scalability**: Multiple workers can process tasks
- **Observability**: Queue depth indicates system health

## 🎯 Success Criteria

### Technical Success

- ✅ All three agents deployed and operational
- ✅ CI/CD pipeline automated
- ✅ Monitoring and alerting configured
- ✅ System handles 100+ transactions/minute

### Business Success

- ✅ Reduces manual financial tasks by 80%
- ✅ Fraud detection accuracy > 95%
- ✅ Credit optimization recommendations accepted > 60%
- ✅ User satisfaction score > 4.5/5

## 📊 Metrics to Track

### System Metrics

- Queue depth (Redis)
- Agent processing time
- API response time
- Database query performance
- Error rates

### Business Metrics

- Recurring payments automated
- Fraud transactions detected
- Credit optimizations recommended
- User notification delivery rate

### AI Metrics

- Gemini API response time
- Decision accuracy
- False positive/negative rates
- Cost per API call

## 🚨 Risk Mitigation

### Technical Risks

- **API Rate Limits**: Implement retry logic and rate limiting
- **Queue Overflow**: Set max queue size and alerts
- **Database Locking**: Optimize queries and use connection pooling
- **Agent Failure**: Health checks and auto-restart

### Business Risks

- **Incorrect Decisions**: Human-in-the-loop for critical decisions
- **Data Privacy**: Encrypt sensitive data and follow regulations
- **Compliance**: Audit logs for all financial actions
- **User Trust**: Transparent notifications and explanations

## 🔄 Future Enhancements

1. **Additional Agents**: Investment recommendations, bill negotiation
2. **Machine Learning**: Train custom models for fraud detection
3. **Mobile App**: Native iOS/Android applications
4. **Voice Interface**: Integration with smart speakers
5. **Blockchain**: Immutable transaction ledger
6. **Advanced Analytics**: Predictive financial insights

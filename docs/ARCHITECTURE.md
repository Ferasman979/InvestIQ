# Architecture Documentation

## System Overview

InvestIQ is a multi-agent banking system that leverages AI to automate critical financial workflows. The architecture follows a microservices pattern where each agent operates independently and communicates through a message queue.

## High-Level Architecture

```
User → Frontend/UI (Streamlit/Next.js)
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

## Component Details

### Frontend Layer

- **Streamlit UI**: Interactive web interface for users to view their financial status
- **Next.js** (optional): Alternative modern frontend framework
- **Purpose**: Provides transparency into agent decisions and allows user interactions

### Backend API Layer

- **Framework**: FastAPI (Python 3.12+)
- **Endpoints**: RESTful API for transaction processing, agent status, notifications
- **Responsibilities**:
  - Receive user requests
  - Route tasks to appropriate agents via message queue
  - Aggregate results from agents
  - Manage authentication and authorization

### Task Routing Layer

- **Technology**: Redis Queue or RabbitMQ
- **Purpose**: Decouple API from agents, enable asynchronous processing
- **Message Types**:
  - Payment execution requests
  - Fraud verification requests
  - Credit optimization triggers

### Agent Layer

Each agent is an independent microservice with its own container:

#### Payment Automation Agent

- **Function**: Identifies and executes recurring payments
- **Logic**: Pattern recognition on transaction history
- **Actions**:
  - Detect recurring payment patterns
  - Schedule automatic execution
  - Alert on insufficient balance

#### Security Verification Agent

- **Function**: Detect and verify fraudulent transactions
- **AI Integration**: Uses Gemini API for transaction analysis
- **Actions**:
  - Analyze transaction patterns
  - Flag suspicious activities
  - Interact with user for verification
  - Block confirmed fraud

#### Credit Optimization Agent

- **Function**: Monitor and optimize credit utilization
- **Logic**: Credit score monitoring, utilization analysis
- **Actions**:
  - Monitor credit score changes
  - Analyze credit utilization
  - Submit credit limit increase requests
  - Optimize credit card usage

### Data Layer

- **Database**: PostgreSQL (production) or SQLite (dev)
- **Schema**:
  - User accounts
  - Transaction history
  - Agent execution logs
  - Credit information
- **Purpose**: Persistent state storage and audit trail

### Notification Layer

- **Email Notifications**: SMTP-based email alerts (Gmail, SendGrid free tier, etc.)
- **In-App Notifications**: Real-time notifications via Streamlit UI or API
- **Notifications Sent**:
  - Payment execution confirmations
  - Fraud alerts
  - Credit optimization recommendations
  - Balance warnings

## Data Flow

1. **User Request**: User initiates action via UI or API
2. **API Processing**: FastAPI receives and validates request
3. **Queue Enqueue**: Request placed in Redis queue
4. **Agent Processing**: Appropriate agent picks up task
5. **AI Reasoning**: Agent uses Gemini API if decision needed
6. **Action Execution**: Agent performs financial action
7. **Database Update**: Results logged to PostgreSQL
8. **Notification**: User notified via Email or In-App UI
9. **Response**: API returns result to user

## Deployment Architecture

### Kubernetes (EKS)

```
┌─────────────────────────────────────┐
│         Kubernetes Cluster          │
│                                     │
│  ┌──────────┐  ┌──────────┐        │
│  │ API Pod  │  │  API Pod │        │
│  └──────────┘  └──────────┘        │
│                                     │
│  ┌──────────┐  ┌──────────┐        │
│  │Payment   │  │Security  │        │
│  │Agent Pod │  │Agent Pod │        │
│  └──────────┘  └──────────┘        │
│                                     │
│  ┌──────────┐                      │
│  │Credit    │                      │
│  │Agent Pod │                      │
│  └──────────┘                      │
└─────────────────────────────────────┘
```

- Each agent runs as a separate Kubernetes pod
- Horizontal scaling based on queue depth
- Health checks and auto-restart
- Service mesh for inter-pod communication

## Security Considerations

- **Authentication**: JWT tokens for API access
- **Authorization**: Role-based access control
- **Data Encryption**: TLS in transit, encryption at rest
- **PII Protection**: Sensitive data masked in logs
- **API Keys**: Securely stored in AWS Secrets Manager
- **Network**: VPC isolation for agent communication

## Scalability

- **Horizontal Scaling**: Agents scale independently based on queue depth
- **Auto-scaling**: Kubernetes HPA based on CPU/memory metrics
- **Load Balancing**: Application load balancer for API layer
- **Database**: Read replicas for read-heavy operations
- **Caching**: Redis cache for frequently accessed data

## Monitoring & Observability

- **Metrics**: Prometheus collects metrics from all pods
- **Logging**: Centralized logging via ELK stack or CloudWatch
- **Tracing**: Distributed tracing for request flow
- **Dashboards**: Grafana dashboards for system health
- **Alerts**: AlertManager for critical issues

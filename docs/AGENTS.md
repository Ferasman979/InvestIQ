# Agents Documentation

This document describes the three autonomous agents that power InvestIQ's banking automation system.

## Agent Overview

Each agent is an independent microservice that:

- Operates as a separate Kubernetes pod
- Processes tasks from Redis queue
- Uses Google Gemini API for decision-making
- Logs all actions to PostgreSQL
- Sends notifications via Email and In-App UI

## Payment Automation Agent

### Purpose

Automatically identifies and executes recurring payments on behalf of users.

### Functionality

1. **Pattern Detection**

   - Analyzes transaction history
   - Identifies recurring payment patterns (monthly, weekly, etc.)
   - Learns user payment preferences

2. **Automatic Execution**

   - Schedules recurring payments
   - Executes payments on due dates
   - Handles payment failures gracefully

3. **Balance Management**
   - Checks account balance before execution
   - Alerts user if balance is insufficient
   - Suggests credit options if needed

### Decision Logic

```python
if is_recurring_payment(transaction):
    if account_balance >= payment_amount:
        execute_payment(transaction)
        notify_user("Payment executed: $amount to $merchant")
    else:
        notify_user("Insufficient balance for $merchant payment")
        suggest_credit_option()
```

### Gemini API Usage

- **Use Case**: Determine if a payment is truly recurring vs. one-time
- **Prompt**: "Is this transaction a recurring payment? Transaction history: ..."
- **Output**: Boolean decision with confidence score

### Notifications

- ✅ Payment executed successfully
- ⚠️ Insufficient balance warning
- 📊 Monthly payment summary

## Security Verification Agent

### Purpose

Detects and prevents fraudulent transactions using AI-powered analysis.

### Functionality

1. **Fraud Detection**

   - Analyzes transaction patterns
   - Flags suspicious activities
   - Uses Gemini API for complex reasoning

2. **User Verification**

   - Sends email alerts for suspicious transactions
   - Displays in-app notifications for immediate visibility
   - Waits for user confirmation
   - Blocks transactions if user denies

3. **Pattern Learning**
   - Learns user spending habits
   - Adapts fraud detection thresholds
   - Reduces false positives over time

### Decision Logic

```python
suspicion_score = analyze_transaction(transaction)
if suspicion_score > threshold:
    decision = query_gemini(transaction_context)
    if decision == "fraudulent":
        block_transaction(transaction)
        notify_user("Blocked suspicious transaction: $amount")
        request_verification()
```

### Gemini API Usage

- **Use Case**: Analyze transaction context and determine if fraudulent
- **Prompt**: "Analyze this transaction for fraud. User history: ..., Transaction: ..., Location: ..."
- **Output**: Fraud probability score and reasoning

### Notifications

- 🚨 Suspicious transaction alert
- ✅ Transaction verified and approved
- 🚫 Transaction blocked

### Fraud Indicators

- Unusual location
- Large amount deviation
- Multiple rapid transactions
- Unknown merchant
- Unusual time of day

## Credit Optimization Agent

### Purpose

Monitors credit utilization and automatically requests credit limit increases when beneficial.

### Functionality

1. **Credit Monitoring**

   - Tracks credit score changes
   - Monitors credit utilization percentage
   - Tracks payment history

2. **Optimization Analysis**

   - Calculates optimal credit utilization
   - Identifies opportunities for limit increases
   - Uses Gemini API to analyze user profile

3. **Automated Requests**
   - Submits credit limit increase requests
   - Tracks approval/rejection
   - Learns from outcomes

### Decision Logic

```python
credit_score = get_credit_score(user_id)
utilization = calculate_utilization(user_id)
eligibility = check_increase_eligibility(credit_score, utilization)

if eligibility:
    reasoning = query_gemini(user_profile, credit_history)
    if reasoning == "recommend_increase":
        submit_increase_request(user_id)
        notify_user("Credit limit increase requested")
```

### Gemini API Usage

- **Use Case**: Determine if credit limit increase would benefit user
- **Prompt**: "Should this user request a credit limit increase? Credit score: ..., Utilization: ..., History: ..."
- **Output**: Recommendation with reasoning

### Notifications

- 📈 Credit score update
- 💳 Credit limit increase request submitted
- ✅ Credit limit increase approved
- 📊 Utilization optimization suggestions

### Credit Optimization Rules

- Maintain utilization below 30%
- Request increases when score improves
- Avoid requests during financial stress
- Space out requests (minimum 6 months)

## Agent Communication

### Message Queue Structure

Each agent subscribes to specific queue channels:

```python
# Payment Agent
redis_queue: "payment_tasks"

# Security Agent
redis_queue: "security_tasks"

# Credit Agent
redis_queue: "credit_tasks"
```

### Task Format

```json
{
  "task_id": "uuid",
  "agent": "payment_agent",
  "action": "execute_recurring_payment",
  "data": {
    "user_id": "123",
    "transaction_id": "456",
    "amount": 100.0
  },
  "priority": "high",
  "created_at": "2025-01-15T10:00:00Z"
}
```

## Agent Metrics

Each agent exposes Prometheus metrics:

- `agent_tasks_processed_total`
- `agent_tasks_failed_total`
- `agent_processing_time_seconds`
- `agent_gemini_api_calls_total`
- `agent_notifications_sent_total`

## Error Handling

### Retry Logic

```python
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

for attempt in range(MAX_RETRIES):
    try:
        result = process_task(task)
        break
    except Exception as e:
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY * (attempt + 1))
            continue
        else:
            log_error(task, e)
            notify_admin("Task failed after retries")
```

### Dead Letter Queue

Failed tasks after max retries are moved to dead letter queue for manual review.

## Testing Agents

### Unit Tests

```bash
cd agents/payment_agent
pytest tests/
```

### Integration Tests

```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration/
```

### Manual Testing

```bash
# Send test task to queue
python scripts/test_agent.py --agent payment_agent --task test_payment.json

# Monitor agent logs
kubectl logs -f deployment/payment-agent -n investiq
```

## Agent Development

### Creating a New Agent

1. Create agent directory: `agents/new_agent/`
2. Create `Dockerfile`
3. Implement `agent.py` with:
   - Queue subscription
   - Task processing logic
   - Gemini API integration
   - Notification sending
4. Add Kubernetes deployment manifest
5. Add monitoring metrics
6. Write tests

### Agent Template

```python
from redis import Redis
from gemini import GeminiClient

class Agent:
    def __init__(self):
        self.redis = Redis.from_url(REDIS_URL)
        self.gemini = GeminiClient(GEMINI_API_KEY)
        self.queue_name = "agent_tasks"

    def process_task(self, task):
        # Agent-specific logic
        decision = self.gemini.analyze(task)
        result = self.execute(decision)
        self.notify_user(result)
        return result

    def run(self):
        while True:
            task = self.redis.blpop(self.queue_name)
            self.process_task(task)
```

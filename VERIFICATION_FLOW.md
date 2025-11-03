# Transaction Verification Flow

This document describes the complete transaction verification workflow aligned with the existing codebase.

## Use Case: Customer Payment Verification

### Flow Overview

```
Customer makes payment
    ↓
Transaction created (status: pending)
    ↓
Automatic verification triggered
    ↓
Suspicious activity check
    ↓
┌─────────────┬─────────────┐
│  Suspicious  │  Not Suspicious │
└─────────────┴─────────────┘
    ↓                ↓
Lock payment      Status remains pending
Send email        (waiting for approval)
Ask security Qs
    ↓
User verifies
    ↓
Transaction status → verified
    ↓
Proceed to vendor
    ↓
Status → approved (completed)
```

## Detailed Flow

### 1. Create Transaction

**Endpoint:** `POST /api/transactions/create_trx`

```json
{
  "amount": 1500.00,
  "vendor": "Amazon",
  "category": "Shopping",
  "date": "2025-01-15"
}
```

**Response:**
```json
{
  "id": 123,
  "amount": 1500.00,
  "vendor": "Amazon",
  "category": "Shopping",
  "tx_date": "2025-01-15",
  "status": "pending",
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

**What happens:**
- Transaction is created in database with status `pending`
- Background task automatically triggers verification
- Verification service checks for suspicious activity

---

### 2. Automatic Verification Check

**Service:** `services/verification_service.py::verify_transaction()`

**Checks performed:**
- Amount thresholds (e.g., > $5000)
- Suspicious merchant names
- Unusual patterns
- Location anomalies
- Time-based anomalies

**Detection Service:** `services/detection_services.py::is_suspicious()`

Returns: `(is_suspicious: bool, reason: str)`

---

### 3A. If Suspicious: Lock Transaction

**Service:** `services/verification_service.py::lock_transaction_for_verification()`

**Actions:**
1. Status remains `pending` (locked for verification)
2. Email sent to user via `services/email_service.py::send_verification_email()`
3. In-app notification created
4. Transaction temporarily locked

**Email contains:**
- Transaction details
- Reason for suspicion
- Link to verification page: `/api/transactions/verify/{tx_id}`

---

### 3B. If Not Suspicious

Transaction status remains `pending`, waiting for explicit approval via:
- Manual approval endpoint
- Or auto-approval logic

---

### 4. User Verification (Security Questions)

**Get Questions:**
**Endpoint:** `GET /api/transactions/verify/{tx_id}/questions`

**Response:**
```json
{
  "transaction_id": 123,
  "questions": [
    "What is your mother's maiden name?",
    "What city were you born in?",
    "What is your favorite pet's name?"
  ],
  "message": "Please answer these security questions to verify the transaction"
}
```

**Verify with Answers:**
**Endpoint:** `POST /api/transactions/verify/{tx_id}`

```json
{
  "transaction_id": 123,
  "answers": {
    "What is your mother's maiden name?": "smith",
    "What city were you born in?": "toronto",
    "What is your favorite pet's name?": "fluffy"
  }
}
```

**Response (Success):**
```json
{
  "verified": true,
  "message": "Transaction verified successfully",
  "transaction_id": 123,
  "status": "verified"
}
```

**Response (Failed):**
```json
{
  "verified": false,
  "message": "Verification failed: 2/3 answers correct",
  "transaction_id": 123,
  "status": "pending"
}
```

**What happens:**
- Answers are verified against user's preset security questions
- If all correct: Status changes to `verified`
- If incorrect: Status remains `pending`, user can retry

---

### 5. Proceed to Vendor

**Endpoint:** `POST /api/transactions/approve_trx/{tx_id}`

```json
{
  "provider_ref": "pay_abc123xyz"  // Optional: external payment reference
}
```

**What happens:**
- Service: `services/verification_service.py::proceed_to_vendor()`
- Calls: `providers/transactions.py::approve_transaction()`
- Status changes: `verified` → `approved`
- Ledger entry created (permanent record)
- Payment sent to vendor
- Confirmation email sent
- In-app notification created

**Response:**
```json
{
  "id": 123,
  "amount": 1500.00,
  "vendor": "Amazon",
  "category": "Shopping",
  "tx_date": "2025-01-15",
  "status": "approved",
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:35:00",
  "ledger_id": 456
}
```

---

## Status Flow

```
pending (created)
    ↓
pending (locked for verification) [if suspicious]
    ↓
verified [after security questions answered correctly]
    ↓
approved [payment sent to vendor]
```

**Alternative path (not suspicious):**
```
pending (created)
    ↓
approved [direct approval without verification]
```

---

## Database Models

### TransactionDB (`models/Transcation.py`)

```python
class TxStatus(str, Enum):
    pending = "pending"      # Created, may be locked for verification
    verified = "verified"    # User verified with security questions
    failed = "failed"        # Verification failed or rejected
    approved = "approved"    # Completed and sent to vendor
```

### TransactionLedger (`models/ledger.py`)

Created when transaction is approved and sent to vendor. Permanent record.

---

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/transactions/create_trx` | POST | Create transaction (auto-verifies) |
| `/api/transactions/get_trx/{tx_id}` | GET | Get transaction details |
| `/api/transactions/approve_trx/{tx_id}` | POST | Approve and send to vendor |
| `/api/transactions/verify/{tx_id}` | POST | Verify with security questions |
| `/api/transactions/verify/{tx_id}/questions` | GET | Get security questions |

---

## Services Structure

### `services/verification_service.py`
- `verify_transaction()` - Check for suspicious activity
- `lock_transaction_for_verification()` - Lock and notify
- `verify_with_security_questions()` - Verify user answers
- `proceed_to_vendor()` - Send to vendor after verification
- `get_security_questions()` - Get questions for user

### `services/detection_services.py`
- `is_suspicious()` - Rule-based anomaly detection

### `services/email_service.py`
- `send_verification_email()` - Send verification email
- `send_approval_email()` - Send approval confirmation

### `services/notification_service.py`
- `send_notification()` - Create in-app notification

---

## Configuration

### Environment Variables Required

```bash
# SMTP Configuration (for emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@investiq.com

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname
```

---

## Security Questions

Currently uses preset questions (TODO: make user-specific):

- "What is your mother's maiden name?"
- "What city were you born in?"
- "What is your favorite pet's name?"

**TODO:**
- Store questions/answers in database per user
- Add user_id to TransactionDB model
- Implement user-specific security questions lookup

---

## Integration with Existing Code

✅ **Aligned with existing code structure:**
- Uses existing `TransactionDB` model and `TxStatus` enum
- Integrates with existing `providers/transactions.py`
- Uses existing notification and email services
- Follows existing router patterns
- Uses existing database session management
- Compatible with existing schemas

✅ **Database-driven:**
- All transactions stored in PostgreSQL
- Status tracked in database
- Ledger entries created for approved transactions

✅ **Background tasks:**
- Verification runs asynchronously after transaction creation
- Doesn't block the API response

---

## Example Complete Flow

```python
# 1. Create transaction
POST /api/transactions/create_trx
{
  "amount": 1500.00,
  "vendor": "SuspiciousMerchant",
  "category": "Shopping",
  "date": "2025-01-15"
}
# Returns: {id: 123, status: "pending"}

# 2. Background verification detects suspicious activity
# Transaction locked, email sent

# 3. Get security questions
GET /api/transactions/verify/123/questions
# Returns: {questions: ["What is your mother's maiden name?", ...]}

# 4. Answer security questions
POST /api/transactions/verify/123
{
  "transaction_id": 123,
  "answers": {
    "What is your mother's maiden name?": "smith",
    "What city were you born in?": "toronto",
    "What is your favorite pet's name?": "fluffy"
  }
}
# Returns: {verified: true, status: "verified"}

# 5. Approve and send to vendor
POST /api/transactions/approve_trx/123
{
  "provider_ref": "pay_abc123"
}
# Returns: {status: "approved", ledger_id: 456}
```

---

This flow is now fully integrated with your existing codebase! 🎉


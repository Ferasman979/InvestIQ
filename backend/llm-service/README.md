# LLM Service - Database Integration

## Overview

The LLM service generates security questions based on transaction data from the PostgreSQL database. It uses Google Gemini to create natural, contextual security questions.

## Prerequisites

- Python 3.12+
- PostgreSQL database (local or EKS)
- Google Gemini API Key

## Setup

### 1. Install Dependencies

```bash
cd backend/llm-service
pip install fastapi uvicorn sqlalchemy psycopg2-binary langchain-google-genai python-dotenv
```

### 2. Configure Environment

Create a `.env` file in `backend/llm-service/`:

```bash
# Database connection (same as main backend)
DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db

# Google Gemini API Key
GOOGLE_API_KEY=your-google-api-key-here
```

**Note:** For EKS, use:
```
DATABASE_URL=postgresql://investiq:investiq123@postgres.investiq.svc.cluster.local:5432/investiq_db
```

### 3. Start the Service

```bash
cd backend/llm-service
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
export GOOGLE_API_KEY=your-api-key-here
uvicorn main:app --port 8000 --reload
```

## Testing

### Quick Test

```bash
# From project root
python3 test_llm_service.py
```

### Manual Test

1. **Start the service:**
   ```bash
   cd backend/llm-service
   uvicorn main:app --port 8000
   ```

2. **Test endpoint:**
   ```bash
   curl -X POST http://localhost:8000/generate-security-question \
     -H "Content-Type: application/json" \
     -d '{}'
   ```

3. **Expected response:**
   ```json
   {
     "security_questions": [
       "Hi, I have blocked your transaction, cuz it seemed suspicious! Please answer a question to verify it's you.\n\nQuestion: Could you tell me the name of the merchant for that Food & Dining transaction yesterday?"
     ],
     "contexts": [
       "Amazon (Shopping) on 2025-11-03\nStarbucks (Food & Dining) on 2025-11-02\nUber (Transportation) on 2025-11-02"
     ]
   }
   ```

### Verify Answer

```bash
curl -X POST http://localhost:8000/verify-security-answer \
  -H "Content-Type: application/json" \
  -d '{
    "user_answer": "Starbucks",
    "question": "Could you tell me the name of the merchant for that Food & Dining transaction yesterday?",
    "context": "Starbucks (Food & Dining) on 2025-11-02"
  }'
```

## Database Schema

The LLM service queries the `transactions` table:

```sql
SELECT vendor as merchant, amount, category, tx_date as transaction_date
FROM transactions
WHERE tx_date >= CURRENT_DATE - INTERVAL '2 days'
ORDER BY tx_date DESC
LIMIT 3
```

**Required columns:**
- `vendor` - Merchant/vendor name
- `amount` - Transaction amount
- `category` - Transaction category
- `tx_date` - Transaction date

## API Endpoints

### POST `/generate-security-question`

Generates security questions based on recent transactions.

**Request:**
```json
{}
```

**Response:**
```json
{
  "security_questions": [
    "Question 1...",
    "Question 2..."
  ],
  "contexts": [
    "Context 1...",
    "Context 2..."
  ]
}
```

### POST `/verify-security-answer`

Verifies user's answer to a security question.

**Request:**
```json
{
  "user_answer": "Starbucks",
  "question": "What was the merchant name?",
  "context": "Starbucks (Food & Dining) on 2025-11-02"
}
```

**Response:**
```json
{
  "result": "true"
}
```

## Troubleshooting

### Database Connection Failed

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Test connection
psql postgresql://investiq:investiq123@localhost:5432/investiq_db -c "SELECT 1"
```

### No Transactions Found

The service requires at least one transaction in the `transactions` table from the last 2 days.

```bash
# Add sample data
cd backend
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
poetry run python scripts/load_csv_data.py ../data/transactions.csv
```

### LLM API Key Error

```bash
# Verify API key is set
echo $GOOGLE_API_KEY

# Or check .env file
cat backend/llm-service/.env | grep GOOGLE_API_KEY
```

### Import Errors

```bash
# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary langchain-google-genai python-dotenv
```

## Development

### Local Development

1. Use local PostgreSQL (docker-compose)
2. Set `DATABASE_URL` to `localhost:5432`
3. Run with `uvicorn main:app --reload`

### EKS Deployment

1. Use EKS database connection string
2. Set `DATABASE_URL` to `postgres.investiq.svc.cluster.local:5432`
3. Deploy as Kubernetes service

## Integration with Main Backend

The LLM service:
- Uses the same database as the main backend
- Reads from the same `transactions` table
- Uses the same `DATABASE_URL` environment variable
- Can be called by the main backend via HTTP

## Notes

- The service queries transactions from the last 2 days
- Returns up to 3 most recent transactions
- Personal details table is not yet implemented (returns None)
- Questions are generated based on transaction context


# Transaction Data Directory

Place your CSV transaction file here for easy loading into the database.

## CSV File Location

**Recommended location:**

```
data/transactions.csv
```

## CSV Format

The CSV loader script automatically detects common column names. Your CSV should include columns for:

### Required Columns:

- **Amount**: `amount`, `Amount`, `transaction_amount`
- **Vendor**: `vendor`, `Vendor`, `merchant`, `Merchant`, `description`
- **Category**: `category`, `Category`, `type`, `Type`
- **Date**: `date`, `Date`, `transaction_date`, `tx_date`

### Optional Columns:

- **Status**: `status`, `Status` (defaults to 'pending' if not provided)

### Example CSV Format:

```csv
amount,vendor,category,date,status
123.45,Amazon,Online Shopping,2024-01-15,pending
67.89,Starbucks,Food & Dining,2024-01-16,approved
234.56,Shell,Gas & Fuel,2024-01-17,pending
```

### Supported Date Formats:

- `YYYY-MM-DD` (e.g., `2024-01-15`)
- `YYYY-MM-DD HH:MM:SS` (e.g., `2024-01-15 10:30:00`)
- `MM/DD/YYYY` (e.g., `01/15/2024`)
- `DD/MM/YYYY` (e.g., `15/01/2024`)

### Supported Amount Formats:

- `1234.56`
- `$1,234.56`
- `1,234.56`

## Loading the CSV

Once you place your CSV file here, load it using:

### Local Development:

```bash
cd backend
export DATABASE_URL=postgresql://investiq:investiq123@localhost:5432/investiq_db
poetry run python scripts/load_csv_data.py ../data/transactions.csv
```

### Kubernetes/EKS:

```bash
# Port-forward PostgreSQL
kubectl port-forward -n investiq svc/postgres 5432:5432

# In another terminal:
cd backend
export DATABASE_URL=postgresql://investiq:changeme@localhost:5432/investiq_db
poetry run python scripts/load_csv_data.py ../data/transactions.csv
```

## Testing with Sample Data

You can test the CSV loader with a small sample first:

```bash
# Load only first 10 rows to test
poetry run python scripts/load_csv_data.py ../data/transactions.csv --max-rows 10

# Validate CSV structure without loading
poetry run python scripts/load_csv_data.py ../data/transactions.csv --dry-run
```

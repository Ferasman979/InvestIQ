# Security Guidelines for Public Repository

## ⚠️ Important: This is a Public Repository

This repository is public, so **NEVER commit** sensitive information such as:

- API keys (Gemini, AWS, etc.)
- Passwords or authentication tokens
- Database credentials
- Private keys or certificates
- Personal information
- Production secrets

## ✅ What's Safe to Commit

The following files are **safe** to commit because they use placeholders or are templates:

- ✅ `infra/kubernetes/secrets.yaml.template` - Template with placeholder values
- ✅ `monitoring/grafana-deployment.yaml` - Uses secret references (but password must be changed)
- ✅ All deployment files with `<dockerhub-username>` placeholders
- ✅ ConfigMaps with example values
- ✅ Docker Compose files (update `.env` file separately)

## 🔒 What to Protect

### Before Pushing, Ensure:

1. **No actual secrets in Kubernetes files:**
   ```bash
   # Check for hardcoded passwords/keys
   grep -r "password.*=" infra/kubernetes/ --include="*.yaml" | grep -v "CHANGE_ME\|your-\|template"
   grep -r "api.*key.*=" infra/kubernetes/ --include="*.yaml" | grep -v "your-\|template\|CHANGE"
   ```

2. **Secrets files are ignored:**
   - `infra/kubernetes/secrets.yaml` (actual secrets - should NOT exist in repo)
   - `monitoring/grafana-secrets.yaml` (if you create one)
   - Any `.env` files with real values

3. **GitHub Secrets configured:**
   - All CI/CD secrets should be in GitHub repository secrets
   - Never hardcode secrets in `.github/workflows/*.yml` files

## 🔧 Pre-Push Checklist

Run these commands before pushing:

```bash
# 1. Check for sensitive files that shouldn't be committed
git status | grep -E "secrets\.yaml$|\.env$|\.key$|\.pem$"

# 2. Verify .gitignore is working
git check-ignore infra/kubernetes/secrets.yaml

# 3. Search for hardcoded passwords (except in templates)
grep -r "admin123\|password.*123\|changeme" --include="*.yaml" --include="*.yml" . | grep -v "template\|CHANGE_ME\|example"

# 4. Verify no actual API keys
grep -r "AIza\|sk-\|AKIA" --include="*.yaml" --include="*.yml" --include="*.py" . | grep -v "your-\|template"
```

## 📝 Required Actions Before Deployment

### 1. Update Grafana Password

Before deploying Grafana, create the secret manually:

```bash
kubectl create secret generic grafana-secrets \
  --from-literal=admin-password=<strong-random-password> \
  --namespace=monitoring
```

Or update the placeholder in `monitoring/grafana-deployment.yaml` before applying, then **DO NOT commit** the updated file.

### 2. Create Application Secrets

```bash
# Create investiq secrets
kubectl create secret generic investiq-secrets \
  --from-literal=gemini-api-key=<your-actual-key> \
  --from-literal=smtp-host=<smtp-host> \
  --from-literal=smtp-port=587 \
  --from-literal=smtp-username=<smtp-user> \
  --from-literal=smtp-password=<smtp-password> \
  --from-literal=email-from=noreply@investiq.com \
  --from-literal=database-user=investiq \
  --from-literal=database-password=<strong-db-password> \
  --namespace=investiq
```

### 3. Update Docker Hub Username

Replace `<dockerhub-username>` in these files:
- `infra/kubernetes/backend-deployment.yaml`
- `infra/kubernetes/payment-agent-deployment.yaml`
- `infra/kubernetes/security-agent-deployment.yaml`
- `infra/kubernetes/credit-agent-deployment.yaml`

### 4. Configure GitHub Secrets

Add these secrets in GitHub repository settings:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_TOKEN`
- `GEMINI_API_KEY`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`

## 🚨 If You Accidentally Commit Secrets

If you accidentally commit secrets:

1. **Immediately rotate/revoke** the exposed credentials
2. Remove from git history:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/secrets.yaml" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. Force push (⚠️ coordinate with team first):
   ```bash
   git push origin --force --all
   ```
4. Consider using `git-secret` or similar tools for future secret management

## 📚 Best Practices

1. **Use Kubernetes Secrets** - Never commit actual secret values
2. **Use GitHub Secrets** - For CI/CD pipelines
3. **Use AWS Secrets Manager** - For production deployments
4. **Review before committing** - Especially YAML and config files
5. **Use pre-commit hooks** - To catch secrets before they're committed
6. **Rotate regularly** - Change passwords and keys periodically

## 🔍 Additional Security Notes

- All Docker images use non-root users for security
- Kubernetes RBAC is configured for Prometheus
- Health checks are configured for all services
- Resource limits prevent resource exhaustion attacks
- Secrets are referenced, not hardcoded in deployments


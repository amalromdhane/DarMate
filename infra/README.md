

## Procédure de Déploiement

### 1. Charger les identifiants AWS Academy
$env:AWS_ACCESS_KEY_ID="VOTRE_ACCESS_KEY"
$env:AWS_SECRET_ACCESS_KEY="VOTRE_SECRET_KEY"
$env:AWS_SESSION_TOKEN="VOTRE_SESSION_TOKEN"
$env:AWS_DEFAULT_REGION="us-east-1"

### 2. Déployer l'infrastructure
cd infra
terraform init
terraform apply -auto-approve

### 3. Tester la démonstration

### 4. Destruction systématique en fin de séance
cd ../scripts
./destroy.ps1


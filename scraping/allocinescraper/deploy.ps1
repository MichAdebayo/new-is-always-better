# Chargement du fichier .env
$ENV_FILE = ".env"
$envVarsMap = @{}
Get-Content $ENV_FILE | Where-Object { $_ -match "=" } | ForEach-Object {
    $parts = $_ -split "=", 2
    $key = $parts[0].Trim()
    $value = $parts[1].Trim()
    $envVarsMap[$key] = $value
}

# Affectation des variables à partir du dictionnaire
$RESOURCE_GROUP = $envVarsMap["RESOURCE_GROUP"]
$CONTAINER_NAME = $envVarsMap["CONTAINER_NAME"]
$ACR_NAME = $envVarsMap["ACR_NAME"]
$IMAGE_NAME = $envVarsMap["IMAGE_NAME"]
$IMAGE_TAG = $envVarsMap["IMAGE_TAG"]
$STORAGE_ACCOUNT_NAME = $envVarsMap["STORAGE_ACCOUNT_NAME"]
$AZURE_STORAGE_CONNECTION_STRING = $envVarsMap["AZURE_STORAGE_CONNECTION_STRING"]
$AZURE_BLOB_CONTAINER_NAME = $envVarsMap["AZURE_BLOB_CONTAINER_NAME"]

# Récupération du login server de l'ACR
$ACR_LOGIN_SERVER = az acr show --name $ACR_NAME --query "loginServer" --output tsv

# Vérification de la présence du fichier Dockerfile
$EXPECTED_FILE = "entrypoint.sh"
if (-not (Test-Path $EXPECTED_FILE)) {
    Write-Error "❌ Le fichier $EXPECTED_FILE est introuvable. Exécute ce script depuis le dossier contenant le Dockerfile."
    exit 1
}

# Connexion à ACR
az acr login --name $ACR_NAME

# Build de l'image
docker build -t "${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}" .

# Push de l'image sur le registre
docker push "${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"

#az container delete --resource-group ncassonetRG --name scraping-job --yes

# Déploiement dans Azure Container Instances
az container create `
  --resource-group $RESOURCE_GROUP `
  --name $CONTAINER_NAME `
  --image "${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}" `
  --registry-login-server $ACR_LOGIN_SERVER `
  --registry-username (az acr credential show --name $ACR_NAME --query "username" --output tsv) `
  --registry-password (az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv) `
  --environment-variables `
    AZURE_STORAGE_CONNECTION_STRING="$AZURE_STORAGE_CONNECTION_STRING" `
    AZURE_BLOB_CONTAINER_NAME="$AZURE_BLOB_CONTAINER_NAME" `
  --restart-policy Never `
  --cpu 1 `
  --memory 1.5 `
  --location "France Central" `
  --os-type Linux

Write-Host "✅ Déploiement terminé !"

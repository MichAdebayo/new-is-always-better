# Force UTF-8 pour éviter les soucis d'affichage
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Chargement du fichier .env
$ENV_FILE = ".env"
$envVarsMap = @{}
Get-Content $ENV_FILE | Where-Object { $_ -match "=" } | ForEach-Object {
    $parts = $_ -split "=", 2
    $key = $parts[0].Trim()
    $value = $parts[1].Trim()
    $envVarsMap[$key] = $value
}

# Variables d'environnement
$RESOURCE_GROUP = $envVarsMap["RESOURCE_GROUP"]
$CONTAINER_NAME = $envVarsMap["CONTAINER_NAME"]
$ACR_NAME = $envVarsMap["ACR_NAME"]
$IMAGE_NAME = $envVarsMap["IMAGE_NAME"]
$IMAGE_TAG = $envVarsMap["IMAGE_TAG"]
$STORAGE_ACCOUNT_NAME = $envVarsMap["STORAGE_ACCOUNT_NAME"]
$AZURE_STORAGE_CONNECTION_STRING = $envVarsMap["AZURE_STORAGE_CONNECTION_STRING"]
$AZURE_BLOB_CONTAINER_NAME = $envVarsMap["AZURE_BLOB_CONTAINER_NAME"]

# Variables fixes
$PLAN_NAME = "scraping-function-plan"
$LOCATION = "France Central"
$FUNCTION_APP_NAME = "scrapingfunctionapp-$(Get-Random)"

# Récupérer le loginServer
$ACR_LOGIN_SERVER = az acr show --name $ACR_NAME --query "loginServer" --output tsv

# Vérifier si le groupe de ressources existe
$resourceGroupExists = az group exists --name $RESOURCE_GROUP
if ($resourceGroupExists -eq "false") {
    az group create --name $RESOURCE_GROUP --location $LOCATION | Out-Null
    Write-Host "[OK] Groupe de ressources créé : $RESOURCE_GROUP"
} else {
    Write-Host "[OK] Le groupe de ressources existe déjà : $RESOURCE_GROUP"
}

# Vérifier si le plan de consommation existe
$planExists = az functionapp plan show --name $PLAN_NAME --resource-group $RESOURCE_GROUP --query "name" --output tsv 2>$null
if (-not $planExists) {
    az functionapp plan create `
        --name $PLAN_NAME `
        --resource-group $RESOURCE_GROUP `
        --location $LOCATION `
        --sku B1 `
        --is-linux | Out-Null
    Write-Host "[OK] Plan de consommation Linux créé : $PLAN_NAME"
} else {
    Write-Host "[OK] Le plan existe déjà : $PLAN_NAME"
}

# Pause de 5 secondes pour laisser Azure enregistrer le plan
Start-Sleep -Seconds 15

# Créer ou recréer la Function App
$functionAppExists = az functionapp show --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --query "name" --output tsv 2>$null
if (-not $functionAppExists) {
    az functionapp create `
        --name $FUNCTION_APP_NAME `
        --resource-group $RESOURCE_GROUP `
        --plan $PLAN_NAME `
        --runtime custom `
        --image "allocineacr.azurecr.io/allocine-scraper-func:v4" `
        --storage-account $STORAGE_ACCOUNT_NAME `
        --functions-version 4 `
        --os-type Linux | Out-Null
    Write-Host "[OK] Function App créée : $FUNCTION_APP_NAME"
} else {
    Write-Host "[Avertissement] Function App déjà existante : $FUNCTION_APP_NAME"
}

# Attente que la Function App soit bien dispo (important pour éviter l'erreur suivante)
Start-Sleep -Seconds 15

# Configurer les variables d'environnement
az functionapp config appsettings set `
    --name $FUNCTION_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --settings `
        AZURE_STORAGE_CONNECTION_STRING="$AZURE_STORAGE_CONNECTION_STRING" `
        AZURE_BLOB_CONTAINER_NAME="$AZURE_BLOB_CONTAINER_NAME" | Out-Null
Write-Host "[OK] Variables d'environnement configurées pour : $FUNCTION_APP_NAME"

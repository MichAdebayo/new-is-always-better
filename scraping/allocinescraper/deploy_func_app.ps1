# Variables personnalisables
$dockerImageName = "allocine-scraper-func"
$dockerImageVersion = "v3"
$acrName = "allocineacr"
$acrLoginServer = "$acrName.azurecr.io"
$functionAppName = "scrapingfunctionapp-785608380"

Write-Host "Build de l'image Docker..."
docker build -t "${dockerImageName}:${dockerImageVersion}" .

Write-Host "Tag de l'image avec ACR..."
docker tag "${dockerImageName}:${dockerImageVersion}" "${acrLoginServer}/${dockerImageName}:${dockerImageVersion}"

Write-Host "Connexion à Azure ACR..."
az acr login --name $acrName

Write-Host "Push de l'image vers Azure Container Registry..."
docker push "${acrLoginServer}/${dockerImageName}:${dockerImageVersion}"

Write-Host "Mise à jour de la Function App avec la nouvelle image..."
az functionapp config container set `
  --name $functionAppName `
  --resource-group ncassonetRG `
  --docker-custom-image-name "${acrLoginServer}/${dockerImageName}:${dockerImageVersion}" `
  --docker-registry-server-url "https://${acrLoginServer}"

Write-Host "Déploiement terminé avec succès !"

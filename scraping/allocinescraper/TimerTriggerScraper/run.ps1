param($Timer)

$currentUTCtime = (Get-Date).ToUniversalTime()

# Si l'exécution est en retard par rapport à l'heure planifiée
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

Write-Host "La fonction de scraping a été déclenchée à : $currentUTCtime"

# Lancer le conteneur Docker pour exécuter le scraping
docker run allocineacr.azurecr.io/allocine-scraper-func:v4

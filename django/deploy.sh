#!/bin/bash

# Création du dossier de logs s'il n'existe pas
mkdir -p logs

# 🔹 Charger les variables depuis le fichier .env
if [ -f .env ]; then
    echo "🔵 Chargement des variables d'environnement depuis .env..."
    export $(grep -v '^#' .env | xargs)  # Charge toutes les variables de .env
else
    echo "⚠️ Fichier .env introuvable ! Assurez-vous qu'il est dans le même dossier."
    exit 1
fi

# 🔹 Utiliser les variables chargées depuis .env
RESOURCE_GROUP="$AZURE_RESOURCE_GROUP"
LOCATION="$AZURE_LOCATION"
ACR_NAME="$AZURE_ACR_NAME"
CONTAINER_NAME="$AZURE_CONTAINER_NAME"
IMAGE_NAME="$AZURE_IMAGE_NAME"
PORT="$AZURE_PORT"
DNS_LABEL="$DNS_LABEL"
CPU="4"
MEMORY="8"

echo "🔵 Connexion à Azure..."
az login | tee logs/azure_login.log

echo "🔵 Vérification du groupe de ressources..."
az group show --name $RESOURCE_GROUP | tee logs/group_show.log || az group create --name $RESOURCE_GROUP --location $LOCATION | tee logs/group_create.log

echo "🔵 Vérification du registre ACR..."
az acr show --name $ACR_NAME | tee logs/acr_show.log || az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic | tee logs/acr_create.log

echo "🔵 Activation de l'administrateur ACR..."
az acr update -n $ACR_NAME --admin-enabled true | tee logs/acr_update.log

echo "🔵 Connexion au registre ACR..."
az acr login --name $ACR_NAME | tee logs/acr_login.log

echo "🔵 Vérification de l'adresse IP publique..."
IP_PUBLIC=$(curl -s ifconfig.me)
echo "Votre adresse IP publique est : $IP_PUBLIC" | tee logs/public_ip.log

echo "🔵 Construction de l'image Docker..."
docker build --build-arg ENV_FILE=.env -t $IMAGE_NAME . | tee logs/docker_build.log

echo "🔵 Tag de l'image Docker..."
docker tag $IMAGE_NAME $ACR_NAME.azurecr.io/$IMAGE_NAME:latest | tee logs/docker_tag.log

echo "🔵 Push de l'image Docker..."
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:latest | tee logs/docker_push.log

echo "🔵 Suppression de l'ancien conteneur (si existant)..."
az container delete --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --yes | tee logs/container_delete.log

echo "🔵 Déploiement du conteneur..."
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_NAME \
  --image $ACR_NAME.azurecr.io/$IMAGE_NAME:latest \
  --ports $PORT \
  --dns-name-label $DNS_LABEL \
  --ip-address Public \
  --registry-username $(az acr credential show --name $ACR_NAME --query "username" -o tsv) \
  --registry-password $(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv) \
  --os-type Linux \
  --cpu $CPU \
  --memory $MEMORY \
  --environment-variables \
      server_="$serverdj_" \
      port_="$portdj_" \
      username_="$usernamedj_" \
      password_="$passworddj_" \
      driver_="$driverdj_" \
      database_="$databasedj_" \
      SECRET_KEY_="$SECRET_KEY_" | tee logs/container_create.log

echo "🔵 Récupération de l'IP publique..."
IP=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query "ipAddress.ip" --output tsv | tee logs/container_ip.log)

echo "✅ Déploiement terminé !"
echo "🌍 Accédez à votre API sur : http://$IP:$PORT/docs"

# Accès via DNS_LABEL
CONTAINER_FQDN="${DNS_LABEL}.${LOCATION}.azurecontainer.io"
echo "Votre application est accessible via : http://${CONTAINER_FQDN}:${PORT}"
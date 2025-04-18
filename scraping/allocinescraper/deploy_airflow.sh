#!/bin/bash

# 👉 Configuration
VM_USER="azureuser"                        # Nom d'utilisateur sur la VM
VM_IP="4.211.87.165"                       # IP publique de ta VM Azure
VM_PROJECT_PATH="/home/azureuser/film-prediction" # Chemin distant du projet
LOCAL_PROJECT_PATH="."                    # Dossier local (projet courant)

echo "🚀 Déploiement Airflow sur la VM Azure..."

# 1. Connexion SSH pour préparer le dossier
echo "📁 Création du dossier sur la VM..."
ssh ${VM_USER}@${VM_IP} "mkdir -p ${VM_PROJECT_PATH}"

# 2. Envoi des fichiers vers la VM
echo "📦 Transfert des fichiers vers la VM..."
scp -r ${LOCAL_PROJECT_PATH}/* ${VM_USER}@${VM_IP}:${VM_PROJECT_PATH}/

# 3. Connexion SSH + Docker Compose up
echo "🐳 Lancement de docker-compose sur la VM..."
ssh ${VM_USER}@${VM_IP} "cd ${VM_PROJECT_PATH} && docker-compose down && docker-compose up -d --build"

echo "✅ Déploiement terminé avec succès !"

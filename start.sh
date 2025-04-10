#!/bin/bash
# Script de démarrage pour l'application de chat sur Lightsail

# Activer l'environnement virtuel (à créer sur le serveur)
source ~/venv/bin/activate

# Démarrer l'application
cd ~/app
uvicorn server_lite:app --host 0.0.0.0 --port 7890

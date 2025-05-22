#!/bin/bash
#set -e

# gcloud config set project YOUR_PROJECT_ID
export PROJECT_ID=$(gcloud config get-value project)
export LOCATION=us-central1

export GOOGLE_GENAI_USE_VERTEXAI=0

#export GOOGLE_GENAI_USE_VERTEXAI=1
#export GOOGLE_CLOUD_PROJECT=$PROJECT_ID
#export GOOGLE_CLOUD_LOCATION=$LOCATION

# Quart debug mode (True or False)
export QUART_DEBUG_MODE=False

# Key
cp keys_dev.txt keys.txt

# build UI
(cd ../../at-ui && npm run build)

# copy UI files
rm -rf ./dist
cp -r ../../at-ui/dist .
#cp -r ../../shop-web-ui/dist .

python3 app.py

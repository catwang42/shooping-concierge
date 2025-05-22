#!/bin/bash
#set -e

# Check if a parameter is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <stage|test>"
  exit 1
fi

# Validate the parameter
if [[ "$1" != "stage" && "$1" != "test" ]]; then
  echo "Error: Parameter must be 'stage' or 'test'"
  exit 1
fi
TAG="$1"

# Copy keys
cp keys_$TAG.txt keys.txt

# To run the app with Vertex AI, use this script as is.
# To run the app with Gemini API key, comment out the following lines.
export PROJECT_ID=$(gcloud config get-value project)
export LOCATION=us-central1

# Agent Framework: Gemini API Key (TODO: replace with Vertex AI)
export GOOGLE_GENAI_USE_VERTEXAI=0

# Quart debug mode (True or False)
export QUART_DEBUG_MODE=False

# build UI
(cd ../../at-ui && npm run build)

# move UI files
rm -rf ./dist
cp -r ../../at-ui/dist .

# build an image
gcr_image_path=gcr.io/$PROJECT_ID/shop_web_$(date +%Y-%m-%d_%H-%M)
gcloud builds submit --tag $gcr_image_path

# deploy (requires at least 1GB memory)
gcloud run deploy shop-web \
  --image $gcr_image_path \
  --platform managed \
  --allow-unauthenticated \
  --project=$PROJECT_ID --region=$LOCATION \
  --set-env-vars=PROJECT_ID=$PROJECT_ID \
  --set-env-vars=LOCATION=$LOCATION \
  --set-env-vars=QUART_DEBUG_MODE=$QUART_DEBUG_MODE \
  --set-env-vars=GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI \
  --tag="$TAG" \
  --min-instances=1 \
  --max-instances=1 \
  --memory 2Gi

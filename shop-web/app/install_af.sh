#!/bin/bash
#set -e

# Installing Agents Framework

#RELEASE_VERSION=20241210
#RELEASE_VERSION=20250204

#gsutil cp gs://agents_v2_hackathon/releases/$RELEASE_VERSION/dist/google_genai_agents-0.0.1.dev$RELEASE_VERSION-py3-none-any.whl .

pip3 uninstall -y google-genai-agents
#pip3 install google_genai_agents-0.0.1.dev$RELEASE_VERSION-py3-none-any.whl
#pip3 install  google_genai_agents-0.0.2.dev20250204+723246417-py3-none-any.whl
pip3 install google_genai_agents-0.0.2.dev20250304+733376416-py3-none-any.whl


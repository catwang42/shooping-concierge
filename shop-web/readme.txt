#
# Install venv (if needed)
#

sudo apt-get update && sudo apt-get install -y python3-venv
python3 -m venv .venv
source .venv/bin/activate

#
# Install pip packages
#

pip install -r requirements.txt
./install_af.sh

#
# Run dev server
#

export GEMINI_API_KEY_DEV=<YOUR KEY>
./run.sh

#
# Stop the dev server
#

pgrep -f "app.py" | xargs kill -1

#
# Deploy
#

export GEMINI_API_KEY_DEPLOY=<YOUR KEY>
./deploy.sh

#
# Install vite 
#

cd /at-ui
npm install -D vite

#
# Embedding generation
#

# generate text embs (edit the SQL before running)
rm nohup.out
nohup python3 shop_data_prep/generate_text_embs.py & 
tail -f nohup.out

# generate mm embs (edit the SQL before running)
rm nohup.out
nohup python3 shop_data_prep/generate_mm_embs.py & 
tail -f nohup.out
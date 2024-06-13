# ai agent for document manipulation
This repository host the document agent

Regions that this deployment can be executed:
- eastus

## Quickstart

```
echo "log into azure dev cli - only once"
azd auth login

echo "provisioning all the resources with the azure dev cli"
azd up

echo "get and set the value for AZURE_ENV_NAME"
azd env get-values | grep AZURE_ENV_NAME
source <(azd env get-values)

echo "building and deploying the agent for phase 1"
bash ./azd-hooks/deploy.sh web $AZURE_ENV_NAME

```

## Questions

look into /mnt/data/phase3_facts.json which contains a list of facts about movies. Based on that list about all the facts you have about the movie with the name "Galactic Adventure" write up a short text of max 500 characters what you know about the movie?


python -m streamlit run app.py --server.port=8000
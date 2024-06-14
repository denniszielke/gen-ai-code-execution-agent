# Secure Dynamic Session for AI Agent code execution
This project demonstrates how to use the Azure Dynamic Session Service to safely execute AI generated code to interact with files in an isolated session.
The code in the repository is using the following technologies:
- Azure OpenAI (as LLM to process user requests and translate them dynamically into Python code)
- Langchain (as as LLM orchestrator to leverage OpenAI and handle tool execution)
- Streamlit (as frontend technology to host the user interface and upload/download files)
- Azure Container Apps (as container runtime for the streamlit application)
- Azure Dynamic Sessions (as host for executing LLM generated python code in a secure session)
- Azure Developer CLI (as means to deploy all resources in the project to Azure)

Here is a high level diagram on how these components work together:

![# reference an image in markdown](architecture.png)

This architecture pattern might be relevant for you if any of the following requirements are applicable for your scenario:
- You need to execute AI generated code on the fly
- You need to isolate tool execution for different user sessions 
- You need to provide dedicated compute/filesystem resources for a user session
- You need to scale out compute sessions in less than a second
- You need to prevent generated code to connect to the network
- You need to provide a secured filesystem per session 

## Quickstart

The recommended way to execute the deployment is to fork the repo and then start a GitHub Codespace because there you will have all the tools to deploy the resources, test the code and try out the whole story end-to-end.
The project resources can be deployed into the following Azure regions:
- eastus

```

echo "log into azure dev cli - only once"
azd auth login

echo "provisioning all the resources with the azure dev cli"
azd up

echo "get and set the value for AZURE_ENV_NAME"
source <(azd env get-values | grep AZURE_ENV_NAME)

echo "building and deploying the streamlit user interface"
bash ./azd-hooks/deploy.sh web $AZURE_ENV_NAME

```

## Run the app locally

Navigate to the folder */src/web*.

```

cd /src/web

echo "installing python packages"
pip install -r requirements.txt

echo "starting app"
python -m streamlit run app.py --server.port=8000

```
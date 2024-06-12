import os

import dotenv
from azure.identity import DefaultAzureCredential
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langchain import agents, hub
from langchain_azure_dynamic_sessions import SessionsPythonREPLTool
from langchain_openai import AzureChatOpenAI

dotenv.load_dotenv()

app = FastAPI()


@app.get("/")
async def root():
    return RedirectResponse("/docs")


@app.get("/chat")
async def chat(message: str):
    credential = DefaultAzureCredential()
    pool_management_endpoint = os.getenv("POOL_MANAGEMENT_ENDPOINT")
    openai_api_key = credential.get_token(
        "https://cognitiveservices.azure.com/.default"
    ).token

    llm = AzureChatOpenAI(
        api_key=openai_api_key,
        azure_deployment="gpt-35-turbo",
        openai_api_version="2024-02-01",
        openai_api_type="azure_ad",
        temperature=0,
    )

    repl = SessionsPythonREPLTool(pool_management_endpoint=pool_management_endpoint)

    tools = [repl]
    prompt = hub.pull("hwchase17/openai-functions-agent")
    agent = agents.create_tool_calling_agent(llm, tools, prompt)

    agent_executor = agents.AgentExecutor(
        agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
    )

    response = agent_executor.invoke({"input": message})

    return {"output": response["output"]}
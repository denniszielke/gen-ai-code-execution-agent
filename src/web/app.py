import os
import dotenv
import pandas as pd
from io import StringIO
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import streamlit as st
from langchain import agents
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_azure_dynamic_sessions import SessionsPythonREPLTool
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent, load_tools
from langchain_community.callbacks.streamlit import (
    StreamlitCallbackHandler,
)
import random

dotenv.load_dotenv()

st.title("💬 AI code execution agent")
st.caption("🚀 A Bot that can run dynamically generated code powered by Langchain, Azure OpenAI and Azure Container Apps")

def get_session_id() -> str:
    id = random.randint(0, 1000000)
    return "00000000-0000-0000-0000-" + str(id).zfill(12)

if "session_id" not in st.session_state:
    st.session_state["session_id"] = get_session_id()
    print("started new session: " + st.session_state["session_id"])

llm: AzureChatOpenAI = None
if "AZURE_OPENAI_API_KEY" in os.environ:
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_deployment=os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME"),
        openai_api_version=os.getenv("AZURE_OPENAI_VERSION"),
        temperature=0,
        streaming=True
    )
else:
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
    llm = AzureChatOpenAI(
        azure_ad_token_provider=token_provider,
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME"),
        openai_api_version=os.getenv("AZURE_OPENAI_VERSION"),
        temperature=0,
        openai_api_type="azure_ad",
        streaming=True
    )


pool_management_endpoint = os.getenv("POOL_MANAGEMENT_ENDPOINT")
repl = SessionsPythonREPLTool(pool_management_endpoint=pool_management_endpoint, session_id=st.session_state["session_id"])

@tool
def download_file(filepath: str) -> str:
    "Download a file from the given path to the user and return the file path"
    filepath = filepath.replace("\n", "")
    filepath = filepath.replace("\"", "")
    filepath = filepath.replace(" ", "")
    filepath = filepath.replace(" ", "")
    filename = os.path.basename(filepath)
    print("Downloading file:-", filename + "-")
    f = repl.download_file(remote_file_path=filename)
    
    st.download_button("Download file", f, file_name=filename)
    return "Sending file: " + filename 
    

tools = [repl, download_file]

if 'file_path' not in st.session_state:
    st.session_state['file_path'] = 'No file found'

st.write("You are running in session: " + st.session_state["session_id"])

promptString = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the original input question you must answer

Thought: you should always think about what to do

Action: the action to take, can be one of [{tool_names}]

Action Input: the input to the action

Observation: the result of the action

... (this Thought/Action/Action Input/Observation can repeat N times)

STOP if you have observed the answer to the original input question

Thought: I now know the final answer

Final Answer: the final answer to the original input question

If there is a reference to a file use the following file in that location: {file_path}
Your work directory for all file operations is /mnt/data/
Only use the download file tool if the user explicitly asks to download the file itself. Otherwise describe to the user what is in the file.

Begin!

Question: {input}

Thought:{agent_scratchpad}
"""
prompt = PromptTemplate.from_template(promptString)

agent = create_react_agent(llm, tools, prompt)
agent_executor = agents.AgentExecutor(
        agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
    )

uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    buffer = StringIO(uploaded_file.getvalue().decode("utf-8"))
    st.write("Uploaded file: ", uploaded_file.name)

    repl.upload_file(data=buffer, remote_file_path=uploaded_file.name)
    st.session_state['file_path'] = '/mnt/data/' + uploaded_file.name

if prompt := st.chat_input():

    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        response = agent_executor.invoke(
            {"input": prompt, "file_path": st.session_state['file_path']}, {"callbacks": [st_callback]}
        )
        st.write(response["output"])

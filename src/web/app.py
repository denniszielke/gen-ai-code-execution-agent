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
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_core.messages import HumanMessage
from langchain_community.callbacks.streamlit import (
    StreamlitCallbackHandler,
)
import random

dotenv.load_dotenv()

st.set_page_config(
    page_title="AI agentic bot that can run dynamically generated code",
)

st.title("💬 AI code execution agent")
st.caption("🚀 A Bot that can run dynamically generated code powered by Langchain, Azure OpenAI and Azure Container Apps")

def get_session_id() -> str:
    id = random.randint(0, 1000000)
    return "00000000-0000-0000-0000-" + str(id).zfill(12)

if "session_id" not in st.session_state:
    st.session_state["session_id"] = get_session_id()
    print("started new session: " + st.session_state["session_id"])
    st.write("You are running in session: " + st.session_state["session_id"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)
    else:
        with st.chat_message("AI"):
            st.markdown(message.content)

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
execute_code_session = SessionsPythonREPLTool(pool_management_endpoint=pool_management_endpoint, session_id=st.session_state["session_id"])

@tool
def do_nothing() -> str:
    "Do nothing"
    return "Done" 

@tool
def send_file(filepath: str) -> str:
    "Send the file from the given path to the user and return the file path"
    filepath = filepath.replace("\n", "")
    filepath = filepath.replace("\"", "")
    filepath = filepath.replace(" ", "")
    filepath = filepath.replace(" ", "")
    filename = os.path.basename(filepath)
    print("Sending file:-", filename + "-")
    f = execute_code_session.download_file(remote_file_path=filename)
    
    st.download_button("Download file", f, file_name=filename, key=filename)
    return "Sending file: " + filename 
    

tools = [execute_code_session, do_nothing, send_file]

if 'file_path' not in st.session_state:
    st.session_state['file_path'] = 'No file found'

promptString = """You are a highly intelligent assistant capable of understanding and executing specific actions based on user requests. Your goal is to assist the user as efficiently and accurately as possible without deviating from their instructions.

Assistant has access to the following tools:

{tools}

Please follow these instructions carefully:

1. If you need to perform an action to answer the user's question, use the following format:
'''
Thought: Do I need to use a tool? Yes
Action: [Specify the action],  should be one of [{tool_names}]
Action Input: [Provide the necessary input for the action]
Observation: [Describe the outcome of the action]
'''

2. If you can answer the user's question without performing any additional actions, use the following format:
'''
Thought: Do I need to use a tool? No
Final Answer: [Provide your answer here]
'''

Your responses should be concise and directly address the user's query. Avoid generating new questions or unnecessary information.

Remember, you do not always need to use tools. Do not provide information the user did not ask for.
End of instructions. Please proceed with answering the user's question following the guidelines provided above.

Begin!

Previous conversation history:

{chat_history}

New input: {input}

{agent_scratchpad}

Only send the file if the user explicitly asks fro a file to be sent.
If there is a reference to a file use the following file in that location: {file_path}
Your work directory for all file operations is /mnt/data/
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

    execute_code_session.upload_file(data=buffer, remote_file_path=uploaded_file.name)
    st.session_state['file_path'] = '/mnt/data/' + uploaded_file.name

human_query = st.chat_input()

if human_query is not None and human_query != "":

    st.session_state.chat_history.append(HumanMessage(human_query))

    with st.chat_message("Human"):
        st.markdown(human_query)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        response = agent_executor.invoke(
            {"input": human_query, "file_path": st.session_state['file_path'], "chat_history": st.session_state.chat_history}, {"callbacks": [st_callback]}, 
        )

        ai_response = st.write(response["output"])

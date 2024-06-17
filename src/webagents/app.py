import os
import dotenv
import pandas as pd
from io import StringIO
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import streamlit as st
from langchain import agents
from langchain_core.prompts import PromptTemplate
from langchain_azure_dynamic_sessions import SessionsPythonREPLTool
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent, load_tools
from langchain_community.callbacks.streamlit import (
    StreamlitCallbackHandler,
)

dotenv.load_dotenv()

st.title("💬 AI Document manipluation agent")
st.caption("🚀 A Streamlit chatbot powered by Langchain, Azure OpenAI and Azure Container Apps")

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
repl = SessionsPythonREPLTool(pool_management_endpoint=pool_management_endpoint)
tools = [repl]
# tools = load_tools(["ddg-search"])

if 'file_path' not in st.session_state:
    st.session_state['file_path'] = 'No file available'

promptString = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer

Thought: you should always think about what to do

Action: the action to take, should be one of [{tool_names}]

Action Input: the input to the action

Observation: the result of the action

... (this Thought/Action/Action Input/Observation can repeat N times)

Thought: I now know the final answer

If there is a reference to a file use the following file in that location: {file_path}
Your work directory for all file operations is /mnt/data/

Final Answer: the final answer to the original input question

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
    # st.write(buffer)

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

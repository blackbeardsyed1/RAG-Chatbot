import os
import pandas as pd
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_experimental.tools import PythonAstREPLTool
from nlp_utils import segment_query
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Any
from mongo import client
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.agents import AgentExecutor
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_astradb import AstraDBVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import create_openai_tools_agent
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain.agents.agent_types import AgentType
import time

from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

# Access variables
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
groq_api_key = os.getenv("groq_api_key")
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_ID = os.getenv("ASTRA_DB_ID")





open = OpenAIEmbeddings(model="text-embedding-3-small")

ASTRA_DB_API_ENDPOINT='https://3b57bc7f-5e7d-4379-88fd-220e27030b42-us-east1.apps.astra.datastax.com/'

vectorstore = AstraDBVectorStore(
    collection_name="pdf_chatter_all",
    embedding=open,
    api_endpoint=ASTRA_DB_API_ENDPOINT,
    token=ASTRA_DB_APPLICATION_TOKEN,
)
retriever3=vectorstore.as_retriever()



retriever_tool2=create_retriever_tool(retriever3,"PdfChatAssistantAgent",
                      "Search for information based on the query and give accurate results.")

tools=[retriever_tool2]


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)


prompt1 = hub.pull("hwchase17/openai-functions-agent")


agent=create_openai_tools_agent(llm,tools,prompt1)

agent_demographic_gpa = create_csv_agent(ChatOpenAI(temperature=0,model='gpt-4o-mini'),
                         'Final_clean_anonymised.csv',
                          agent_type=AgentType.OPENAI_FUNCTIONS,
                          
                         verbose=True)

agentt_FA14_SP17 = create_csv_agent(ChatOpenAI(temperature=0,model='gpt-4o-mini'),
                         r'C:\Users\BOOTYHUNTER\Desktop\FinalChatBot\src\Internal_Record_FA14_to_SP17_csv_1.csv',
                          agent_type=AgentType.OPENAI_FUNCTIONS,
                          
                         verbose=True)


agentt_FA17_FA20 = create_csv_agent(ChatOpenAI(temperature=0,model='gpt-4o-mini'),
                         r'C:\Users\BOOTYHUNTER\Desktop\FinalChatBot\src\Internal_Record_FA17_to_FA20_csv_1.csv',
                          agent_type=AgentType.OPENAI_FUNCTIONS,
                       
                         verbose=True)

agentt_FA21_FA23 = create_csv_agent(ChatOpenAI(temperature=0,model='gpt-4o-mini'),
                         r'C:\Users\BOOTYHUNTER\Desktop\FinalChatBot\src\Internal_Record_FA21_to_FA23_csv_1.csv',
                          agent_type=AgentType.OPENAI_FUNCTIONS,
                                   
                         verbose=True)


agent_executor=AgentExecutor(agent=agent,tools=tools,verbose=True)

db = client['InfoDissemnation']
collection_name = 'records'
collection = db[collection_name]


# query = input(str("Please enter your query \n: "))

# result = segment_query(query)
# print(result)

# result
# merged_queries = {}

# # Iterate through each result
# for resul in result:
#     option = resul['option']
#     query = resul['query']

#     # If the option is already in the dictionary, append the query
#     if option in merged_queries:
#         merged_queries[option] += ' ' + query  # Add a space before appending the new query
#     else:
#         merged_queries[option] = query  # Create a new entry

# # Convert the merged queries back into a list of dictionaries
# result = [{'option': option, 'query': merged_queries[option]} for option in merged_queries]

# Print the merged results
# print(result)

formatter=' DO NOT GIVE ME CODE BLOCKS OR RESULT IN BACKTICS AS A RESULT, RATHER GIVE THE RESULT AS PLAIN STRINGS IN THE OUTPUT TO THE QUESTION ASKED AFTER COMPUTING THE ANSWER YOURSELF.'

# Dictionary to store results from each agent
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify frontend origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model to validate the incoming raw query string
class QueryRequest(BaseModel):
    query: str

@app.post("/process-queries/")
async def process_queries(request: QueryRequest):
    # Segment the raw query into structured `result`
    result = segment_query(request.query)

    # Merge queries with the same option
    merged_queries = {}
    for resul in result:
        option = resul['option']
        query = resul['query']
        print(option,' ',query)
        if option in merged_queries:
            merged_queries[option] += ' ' + query  # Add a space before appending the new query
        else:
            merged_queries[option] = query

    # Convert merged queries back into a list of dictionaries
    result = [{'option': option, 'query': merged_queries[option]} for option in merged_queries]

    # Initialize the dictionary to store results from each agent
    agent_results = {
        '1': None,
        '2': None,
        '3': None,
        '4': None,
        '5': None,
        '6': None
    }
    try:
        # Process each query in the merged result based on the option
        for item in result:
            option = str(item['option'])
            if option != '6':
                query = item['query'] + formatter
            else:
                query = item['query']
            if option == '1':
                print('Entering 14 to 17 spring')
                agent_results['1'] = agentt_FA14_SP17.run(query)
            elif option == '2':
                print(query)
                print('Entering 17 to 20')
                agent_results['2'] = agentt_FA17_FA20.run(query)
            elif option == '3':
                try:
                    response = agentt_FA21_FA23.run(query)
                except Exception as e:
                    response = str(e)
                    if response.startswith("Could not parse LLM output: `"):
                        response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")
                        print(response)
                print('Entering 21 to 23 ')
                agent_results['3'] = response
            elif option == '4':
                try:
                    response = agent_demographic_gpa.run(query)
                except Exception as e:
                    response = str(e)
                    if response.startswith("Could not parse LLM output: `"):
                        response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")
                        print(response)
                agent_results['4'] = response
            elif option == '5':
                record = [{"timestamp": datetime.now(), "description": query}]
                try:
                    data_inserted = collection.insert_many(record)
                    print("Information Sent to the database.")
                except Exception as e:
                    print("Error inserting records:", e)
            elif option == '6':
                agent_results['6'] = agent_executor.invoke({"input": query})['output']
        
        # Generate the final output if all queries succeed
        final_output = ' '.join(str(value) for value in agent_results.values() if value)
        return {"final_output": final_output}

    except Exception as e:
        # If any part of the loop fails, return an error message
        raise HTTPException(status_code=500, detail="Kindly enter the query again, there was a problem processing.")

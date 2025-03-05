import os
import streamlit as st
from chroma_utils import vector_store
# import sys
# sys.path.insert(0, 'C:/Users/Ruchitesh/Desktop/')
# from my_key import grq_key
# os.environ["GROQ_API_KEY"]=grq_key
from langchain_groq import ChatGroq
# from ui import api_key
retriever = vector_store.as_retriever(search_kwargs={"k":2})

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
chat_history = []
contextualize_system_prompt = ("Given chat history and the latest user question"
                               "You need to refine the question bank as per the requirment of the user. "
                               "if required form stand alone question otherwise return as it is.")
contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
qa_prompt=ChatPromptTemplate.from_messages(
    [
        ("system",'''You are a helpful assistant to a paper setter for the university exam. The question bank is provided as {context}. Your task is to generate questions on {input} with the same level of difficulty as the question bank. You can modify numeric values from {context}.

Your generated questions should include applied scenarios from all levels of Bloom's Taxonomy. Each question must be mapped to one of the following course outcomes: {co} (choose one).

For each question, also include the relevant Bloom's Taxonomy level as:

N for Analyze
A for Apply
E for Evaluate
R for Remember
U for Understand
C for Create
Your output should only include:

The question
The corresponding Bloom's Taxonomy level
The mapped course outcome (e.g., CO1, CO2, etc.) if {co} is None do not write course outcome in output. 
Do not include anything else''')
        ,
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ]
)
# follow_up_question = "comparision of it with forwarding"
def generate_response(question,course_outcomes,chat_history,model):
    llm = ChatGroq(
        model_name=model,
        api_key=st.secrets["GROQ_API_KEY"],
        temperature=0
    )
    history_aware_retriver = create_history_aware_retriever(llm, retriever, contextualize_prompt)
    question_answer_chain=create_stuff_documents_chain(llm,prompt=qa_prompt)
    chain=create_retrieval_chain(history_aware_retriver, question_answer_chain)
    response= chain.invoke({"input":  question,"co":course_outcomes, "chat_history":chat_history})
    chat_history.extend([HumanMessage(content=question), response["answer"]])
    return response["answer"]

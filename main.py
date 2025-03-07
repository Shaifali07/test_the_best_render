import streamlit as st
import os
import pathlib
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from langchain_utilites import generate_response
from db_utilities import get_chat_history,insert_application_logs,get_all_documents
from pydantic import BaseModel
from chroma_utils import index_document_to_Chroma
import uuid
import torch
torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)]
# from fastapi import FastAPI, UploadFile, File,HTTPException
# app=FastAPI()


# directory_path=os.path.join(pathlib.Path(__file__).parent.resolve(),'\papers')
directory_path=(os.getcwd()+'/papers')

def clear_question_bank(directory_path):
    try:

        files = os.listdir(directory_path)
        for file in files:
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return True
    except OSError:
         return False
if (not clear_question_bank(directory_path)):
    print("error in clearing the question bank")

from db_utilities import insert_document_record, delete_all_record
delete_all_record()
clear_question_bank(directory_path)

directory_path=(os.getcwd()+'/papers')

st.title("Paper Genie :male_genie: : Test the Best :pencil: ")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None

def create_upload_file(uploaded_file_name, uploaded_file):
    try:

        file_path = os.getcwd() + '/papers/' + uploaded_file_name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        success = index_document_to_Chroma()
        file_id = insert_document_record(uploaded_file_name)
        if (success):
            return True
        else:
            return False

    except Exception as e:
        return {"message": e.args}


def upload_document(uploaded_files):
    try:
        for i in range(len(uploaded_files)):
            response = create_upload_file(uploaded_files[i].name, uploaded_file[i])
            if not response:
                return "error in uploading"+ uploaded_files[i].name
            index_document_to_Chroma()
            insert_document_record(uploaded_files[i].name)
        return "Files saved Successfully"
    except Exception as e:
        st.error(f"An error occurred while uploading the file: {str(e)}")
        return None
def chat(question, course_outcomes,session_id, model):
    if(session_id):
        session_id = str(uuid.uuid4())
    chat_history =get_chat_history(session_id)
    response = generate_response(question, course_outcomes, chat_history,model)
    insert_application_logs(session_id, question, response, model)
    return response
def get_chat_response(question, course_outcomes,session_id, model):
    # headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    # if (course_outcomes==None):
    #     data = {"question": question, "model": model}
    # else:
    #     data = {"question": question, "course_outcomes":course_outcomes,"model": model}
    # # st.write(data)
    # if session_id:
    #     data["session_id"] = session_id

    try:
        response = chat(question, course_outcomes, session_id, model)
        if response:
            return response,session_id
        else:
            st.error("Error in generating response")
            return None

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

model_options = ["DeepSeek-R1-Distill-Llama-70b", "llama-3.3-70b-versatile","gemma2-9b-it:Google"]
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
st.sidebar.selectbox("Select Model", options=model_options, key="model")

uploaded_file = st.sidebar.file_uploader("Add Question Bank", type=["docx"],accept_multiple_files=True,key=st.session_state.uploader_key)
if uploaded_file and st.sidebar.button("Upload"):
    with st.spinner("Uploading..."):
        upload_response = upload_document(uploaded_file)
        st.sidebar.write(f":green[{upload_response}]")
st.sidebar.header("Uploaded Documents")

if st.sidebar.button("List Documents"):
      st.session_state.documents = get_all_documents()
      # st.write(st.session_state.documents)
      if (len(st.session_state.documents)==0):
          st.sidebar.write(":red[Please Upload the Question Bank]")
if "documents" in st.session_state and st.session_state.documents:
     for doc in st.session_state.documents:
        st.sidebar.text(f"{doc['filename']} (ID: {doc['id']})")

if st.sidebar.button("Clear Question Bank"):
    clear_question_bank(directory_path)
    delete_all_record()
    st.session_state.documents=None
    st.session_state.uploader_key+=1
    st.rerun()

if "key_text" not in st.session_state:
    st.session_state.key_text='text'
user_input = st.sidebar.text_area("Enter Course Outcomes:(co1:xxx,co2:yyy)", key=st.session_state.key_text)
col1, col2 = st.sidebar.columns(2)
with col1:
    add_co_button=col1.button("Add COs")
if add_co_button and user_input:
        text=st.sidebar.text_area("You have entered",user_input)
with col2:
    clear_co_button=col2.button("Clear COs")
    if(clear_co_button):
        st.session_state.key_text = st.session_state.key_text+'0'
        st.rerun()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

    # Handle new user input
if prompt := st.chat_input("Query:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get API response
    with st.spinner("Generating response..."):
        response, ses_id = get_chat_response(prompt, user_input, st.session_state.session_id, st.session_state.model)
        # st.write(st.session_state.model)

        if response:
            st.session_state.session_id = ses_id
            st.session_state.messages.append({"role": "assistant", "content": response})
            # st.write(response.get('model'))

            with st.chat_message("assistant"):
                st.markdown(response)
# class query_input(BaseModel):
#     question:str
#     course_outcomes:str=None
#     session_id: str = None
#     model:str = "llama-3.3-70b-versatile"
# class QueryResponse(BaseModel):
#     response: str
#     session_id: str
#     model_name:str

# @app.post("/chat", response_model=QueryResponse)
# async def chat(query_input:query_input):
#     if(not query_input.session_id):
#         query_input.session_id = str(uuid.uuid4())
#     chat_history =get_chat_history(query_input.session_id)
#     response = generate_response(query_input.question, query_input.course_outcomes, chat_history,query_input.model)
#     insert_application_logs(query_input.session_id, query_input.question, response, query_input.model)

#     return QueryResponse(response=response, session_id=query_input.session_id, model_name=query_input.model)

# @app.get("/listfile")
# async def list_files():
#     documents = get_all_documents()
#     return documents





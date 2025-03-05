# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import requests
import os
import pathlib
import torch
from db_utilities import get_all_documents, delete_all_record
from main import clear_question_bank

# os.environ["GROQ_API_KEY"]=
torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)] 
directory_path=os.path.join(pathlib.Path(__file__).parent.resolve(),'\papers')
# from sidebar import display_sidebar
# from chat_interface import display_chat_interface

st.title("Paper Genie :male_genie: : Test the Best :pencil: ")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None
def upload_document(uploaded_files):
    try:
        # Prepare the files for sending to the FastAPI endpoint
        # files_dict = {'files': []}

        # Add the files to the dictionary as (filename, file object) tuples
        # for file in uploaded_files:

        for i in range(len(uploaded_files)):
            files_dict = {"file": (uploaded_files[i].name, uploaded_file[i], uploaded_file[i].type)}
            response = requests.post("http://localhost:8000/uploadfile", files=files_dict)
            # st.write(response)
        # print([(uploaded_files[i].name, uploaded_files[i]) for i in range(len(uploaded_files))])# files=[]
        # for i in range(len(uploaded_file)):
        #        files.append(("file", uploaded_files[i].getvalue()))
        # print(len(files))
        # print(files)

        if response.status_code == 200:
            return "File(s) Saved Successfully!!!!!"
        else:
            st.error(f"Failed to upload file. Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while uploading the file: {str(e)}")
        return None
def get_api_response(question, course_outcomes,session_id, model):
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    if (course_outcomes==None):
        data = {"question": question, "model": model}
    else:
        data = {"question": question, "course_outcomes":course_outcomes,"model": model}
    # st.write(data)
    if session_id:
        data["session_id"] = session_id

    try:
        response = requests.post("http://localhost:8000/chat", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            st.error(f":red[Please upload the question bank.]")
            return None
        else:
            st.error(f"API request failed with status code {response.status_code}: {response.text}")
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
        response = get_api_response(prompt,user_input, st.session_state.session_id, st.session_state.model)
        # st.write(st.session_state.model)

        if response:
            st.session_state.session_id = response.get('session_id')
            st.session_state.messages.append({"role": "assistant", "content": response['response']})
            # st.write(response.get('model'))

            with st.chat_message("assistant"):
                st.markdown(response['response'])




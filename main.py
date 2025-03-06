import os
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





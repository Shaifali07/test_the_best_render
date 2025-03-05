from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

text_splitter=RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20,
    length_function=len
)
embedding_function=HuggingFaceEmbeddings()
persist_directory=r"db"
vector_store = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
def load_documents():
    loader = DirectoryLoader(r"papers", glob="**/*.docx")
    total_docs=len(loader.load())
    splits = loader.load_and_split(text_splitter=text_splitter)
    return splits,total_docs

def index_document_to_Chroma():
    try:
        splits,total_docs = load_documents()
        vector_store.add_documents(splits)
        return True
    except Exception as e:
        print(f"Error indexing document: {e}")
        return False
    # splits,total_docs=load_documents()
    # # document_embedings=embedings.embed_documents([split.page_content for split in splits])
    # vectorstore.add_documents(splits)
    # # vector_store=Chroma.from_documents(
    # #     documents=splits,
    # #     embedding=embedings,
    # #     persist_directory=persist_directory
    # # )
    # return vector_store,total_docs


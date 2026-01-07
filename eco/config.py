import os

import dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

dotenv.load_dotenv()

class Config:
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL')
    OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL')
    chatOpenAI = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    embedding_model = OpenAIEmbeddings(model=os.getenv('OPENAI_EMBEDDINGS_MODEL'))
    MILVUS_URL = os.environ.get('MILVUS_URL')
    MILVUS_PORT = int(os.environ.get('MILVUS_PORT'))
    MILVUS_TOKEN = os.environ.get('MILVUS_TOKEN')

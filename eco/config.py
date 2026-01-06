import os

import dotenv
from langchain_openai import ChatOpenAI
dotenv.load_dotenv()

class Config:
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL')
    OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL')
    chatOpenAI = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
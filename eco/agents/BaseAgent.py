from langchain_core.messages import BaseMessage, AIMessage
from langchain_milvus import Milvus

from eco.config import Config


class BaseAgent:
    SR = "structured_response"
    milvus_connection_args = {"uri": f"{Config.MILVUS_URL}:{Config.MILVUS_PORT}", "token": Config.MILVUS_TOKEN,
                              "db_name": 'eco'}

    def buildMessage(self, msg: list[BaseMessage]):
        return {"messages": msg}

    def getLoadedVectorStore(self, collection_name):
        return Milvus(
            Config.embedding_model,
            connection_args=self.milvus_connection_args,
            collection_name=collection_name,
        )

    def getAIMessageInRes(self,res):
        for m in res.get('messages',[]):
            if isinstance(m,AIMessage):
                return m.content
        return None
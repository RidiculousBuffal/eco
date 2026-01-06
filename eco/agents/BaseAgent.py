from langchain_core.messages import BaseMessage


class BaseAgent:
    SR = "structured_response"
    def buildMessage(self,msg:list[BaseMessage]):
        return {"messages":msg}
import asyncio
from typing import Literal

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from eco.agents.BaseAgent import BaseAgent
from eco.config import Config
from eco.data.preprocess import Data


class ROIdistillation(BaseAgent):

    def __init__(self, ):
        self.agent = create_agent(Config.chatOpenAI, response_format=self.ROIdisstillationModel)
        self.embedding_model = Config.embedding_model

    async def call(self, slow_code, fast_code)->"ROIdisstillationModel":
        prompt = self.get_ROI_Distillation_prompt(slow_code, fast_code)
        message = HumanMessage(content=prompt)
        res = await self.agent.ainvoke(self.buildMessage([message]))
        return res[self.SR]



    class ROIdisstillationModel(BaseModel):
        description: str = Field(
            description="Briefly describe the inefficiency in slow_code and how fast_code fixes it.")
        runtime_improvement: int = "Integer (1-10) rating of runtime gain."
        category: Literal[
            "Algorithm", 'Data Structure', 'Memory Management', 'Code Execution', 'System Interaction', 'Other']

    def get_ROI_Distillation_prompt(self, slow_code, fast_code):
        return f"""
    Identify each optimization in the Slow Code and explain how it speeds up the Fast Code. 
    Respond in JSON array form, with objects containing:
    [
      {{
        "description": "Briefly describe the inefficiency in slow_code and how fast_code fixes it.",
        "runtime_improvement": "Integer (1-10) rating of runtime gain.",
        "category": "One of: Algorithm | Data Structure | Memory Management | Code Execution | System Interaction | Other"
      }},
      ...
    ]
    Slow Code:
    {slow_code}
    Fast Code:
    {fast_code}
    """

if __name__ == '__main__':
    async def main():
        d = Data()
        data = d.getProcessedData()
        r = ROIdistillation()
        test = data[0]
        res = await r.call(test.src_code,test.tgt_code)
        print(res)
    if __name__ == '__main__':
        asyncio.run(main())
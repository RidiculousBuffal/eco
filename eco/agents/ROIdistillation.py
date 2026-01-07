import asyncio
from typing import Literal, List

from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from eco.agents.BaseAgent import BaseAgent
from eco.config import Config
from eco.data.preprocess import Data


class ROIdisstillationModel(BaseModel):
    description: str = Field(
        description="Briefly describe the inefficiency in slow_code and how fast_code fixes it.")
    runtime_improvement: int = Field(description="Integer(1-10) rating of runtime gain.")
    category: Literal[
        "Algorithm", 'Data Structure', 'Memory Management', 'Code Execution', 'System Interaction', 'Other']


class ROIS(BaseModel):
    rois: list[ROIdisstillationModel] = Field("all ROIS")


class ROIdistillation(BaseAgent):

    def __init__(self, ):
        self.agent = create_agent(Config.chatOpenAI,
                                  response_format=ROIS)
        self.embedding_model = Config.embedding_model
        self.vector_store = self.getLoadedVectorStore("roi")

    async def call(self, slow_code, fast_code) -> ROIS:
        prompt = self.get_ROI_Distillation_prompt(slow_code, fast_code)
        message = HumanMessage(content=prompt)
        res = await self.agent.ainvoke(self.buildMessage([message]))
        return res[self.SR]

    async def embeddingROI(self, roi: ROIS, metadata: Data.TrainHQ):

        document = Document(page_content=roi.model_dump_json(), metadata={"metadata": metadata.model_dump()})
        doc_id = f"{metadata.src_id}-{metadata.tgt_id}"
        if len(roi.model_dump_json()) < 65530 and len(metadata.model_dump_json()) < 65530:
            self.vector_store.add_documents(documents=[document], ids=[doc_id])
        return document, doc_id

    async def batchEmbeddingROI(self, rois: list[ROIS], metadatas: list[Data.TrainHQ]):
        if len(rois) != len(metadatas):
            return
        documents = []
        doc_ids = []
        for i in range(0, len(rois)):
            if len(rois[i].model_dump_json()) > 65530 or len(metadatas[i].model_dump_json()) > 65530:
                continue
            document = Document(page_content=rois[i].model_dump_json(),
                                metadata={"metadata": metadatas[i].model_dump()})
            doc_id = f"{metadatas[i].src_id}-{metadatas[i].tgt_id}"
            documents.append(document)
            doc_ids.append(doc_id)
        self.vector_store.add_documents(documents=documents, ids=doc_ids)
        return documents, doc_ids

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
        res = await r.call(test.src_code, test.tgt_code)
        print(res)
        print(res.model_dump())


    if __name__ == '__main__':
        asyncio.run(main())

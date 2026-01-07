import asyncio

from langchain.agents import create_agent

from eco.agents.ROIRetriever import ROIRetriever
from eco.config import Config
from eco.joern.JoernDetector import JoernAdvisor


class ECOAgent:
    def __init__(self):
        self.agent = create_agent(Config.chatOpenAI)
        self.joern_detector = JoernAdvisor()
        self.roi_retriever = ROIRetriever()

    async def _retrieve_task(self, input_code):
        performance_opt = await self.roi_retriever.generate_performance_related_distillation(input_code)
        res = await self.roi_retriever.retrieve_from_vdb(performance_opt)
        return [r[0] for r in res]

    async def build_prompt(self, input_code):
        joern_task = self.joern_detector.analyze_code(input_code)
        retrieve_task = self._retrieve_task(input_code)
        joern_res,retrieve_res = await asyncio.gather(joern_task, retrieve_task)
        prompt = (f"""
Given a program and optimization tips, optimize the program and provide a more efficient version.
### Original code:
{input_code}\n"""
+f"""### BottleNecks [detected by joern]:\n"""
+'\n'.join(joern_res)
+f"""### Performance-related characteristics \n""")


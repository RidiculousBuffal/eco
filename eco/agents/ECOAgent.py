import asyncio

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from eco.agents.BaseAgent import BaseAgent
from eco.agents.ROIRetriever import ROIRetriever
from eco.config import Config
from eco.joern.JoernDetector import JoernAdvisor


class ECOAgent(BaseAgent):
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
        joern_res, retrieve_res = await asyncio.gather(joern_task, retrieve_task)
        prompt = (
                    f"""Given a program and optimization tips, optimize the program and provide a more efficient version.\n### Original code:\n{input_code}\n"""
                    + f"""### BottleNecks [detected by joern]:\n"""
                    + '\n'.join(joern_res)
                    + f"""### Performance-related characteristics \n""")
        for i in range(0, len(retrieve_res)):
            prompt += f"======================={i}:=======================\n"
            prompt += f"slow_code:\n" + retrieve_res[i].metadata.get("metadata", {}).get("src_code", "") + '\n'
            prompt += f"fast_code:\n" + retrieve_res[i].metadata.get("metadata", {}).get("tgt_code", "") + '\n'
            prompt += f"runtime optimization instructions:\n" + retrieve_res[i].page_content + '\n'
        return prompt

    async def call(self, input_code):
        human_message = HumanMessage(content=await self.build_prompt(input_code))
        await self.agent.ainvoke(self.buildMessage([human_message]))


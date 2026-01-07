import asyncio

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from eco.agents.BaseAgent import BaseAgent
from eco.config import Config


class ROIRetriever(BaseAgent):
    def __init__(self,):
        self.vector_store = self.getLoadedVectorStore("roi")
        self.SYSTEM_PROMPT = r"""You are a competitive-programming performance analyst.

### Task
1. A **slow C++ program** is given between ```cpp``` blocks below.
2. Analyse it **only from a runtime-performance standpoint** - do **NOT** propose fixes or rewrites.
3. Identify every major **bottleneck** that contributes to slower runtime.
4. Cover these angles where applicable:
    * algorithmic complexity
    * data-structure choiceb
    * I/O or library usage
    * memory-access patterns / allocations
5. For each bottleneck, estimate its relative impact on a **1-10 scale** (10 = largest slowdown factor)."""
        self.agent = create_agent(Config.chatOpenAI)

    async def generate_performance_related_distillation(self,input_code):
        systemMessage = SystemMessage(content=self.SYSTEM_PROMPT)
        humanMessage = HumanMessage(content=f"```cpp\n{input_code}\n```")
        res = await self.agent.ainvoke(self.buildMessage([systemMessage,humanMessage]))
        for m in res.get('messages',[]):
            if isinstance(m,AIMessage):
                return m.content
        return None
    async def retrieve_from_vdb(self,performance_opt):
        return self.vector_store.similarity_search_with_score(performance_opt, 4)


if __name__ == '__main__':
    async def main():
        agent = ROIRetriever()
        res = await agent.generate_performance_related_distillation(input_code='''#include <iostream>\n\n\n\nusing namespace std;\n\n\n\nint main()\n\n{\n\n    for(int i=1;i<=9;i++)\n\n    {\n\n        for(int j=1;j<=9;j++)\n\n            {\n\n            cout<<i<<\"x\"<<j<<\"=\"<<(i*j)<<endl;\n\n            }\n\n    }\n\n    return 0;\n\n}''')
        print(res)
        print("=====")
        retrieved = await agent.retrieve_from_vdb(res)
        for r in retrieved:
            print("======================")
            print(r[0].page_content)
            print(r[0].metadata.get("metadata"))
            print(r[1])
            print("======================")
    asyncio.run(main())
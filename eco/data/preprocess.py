import json
import os

from pydantic import BaseModel

"""
{"src_id":"s794463430",
"tgt_id":"s390430969",
"src_agg_runtime":0.0010421574,
"tgt_agg_runtime":0.0002137555,
"problem_id":"p00000",
"speedup":4.8754637763,
"src_code":"#include <iostream>\n\n\n\nusing namespace std;\n\n\n\nint main()\n\n{\n\n    for(int i=1;i<=9;i++)\n\n    {\n\n        for(int j=1;j<=9;j++)\n\n            {\n\n            cout<<i<<\"x\"<<j<<\"=\"<<(i*j)<<endl;\n\n            }\n\n    }\n\n    return 0;\n\n}",
"tgt_code":"#include<stdio.h>\n\n\n\nint main()\n\n{\n\n    int i,j,mt=0;\n\n\n\n    for(i=1;i<10;i++)\n\n    {\n\n        for(j=1;j<10;j++)\n\n        {\n\n           mt = i * j;\n\n           printf(\"%dx%d=%d\\n\",i,j,mt);\n\n        }\n\n\n\n    }\n\n    return 0;\n\n}",
"fastest_agg_runtime":0.0002134063,
"target_reward":0.9983663301,
"src_reward":0.9995786358,
"src_status":"Accepted",
"tgt_status":"Accepted",
"user_id":"u011621222",
"speedup_v2":4.8754637763}
"""

class Data:
    filePath = os.path.join(os.path.dirname(os.path.realpath(__file__)),'train_hq_only.jsonl')
    class TrainHQ(BaseModel):
        src_id: str
        tgt_id: str
        src_agg_runtime: float
        tgt_agg_runtime: float
        problem_id: str
        speedup: float
        src_code: str
        tgt_code: str
        fastest_agg_runtime: float
        target_reward: float
        src_reward: float
        src_status: str
        tgt_status: str
        user_id: str
        speedup_v2: float


    def getProcessedData(self):
        with open(self.filePath, 'r') as f:
            data = [self.TrainHQ.model_validate(json.loads(line)) for line in f]
        return data



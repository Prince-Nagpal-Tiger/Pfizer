import sys
sys.path.append("D:/pfizer_demo")
from agents.base_agent import BaseAgent
from agents.prompts import ExperimentPrompt
from utils import create_data
import re
import json

class ExperimentAgent(BaseAgent):
    
    def __init__(self, client, prompt=ExperimentPrompt, model=None):
        if model is None:
            super().__init__(prompt=prompt, client=client)
        else:
            super().__init__(prompt=prompt, client=client, model=model)
    
    def extract_output(self, llm_response):
        pattern = r"```json(.*?)```"
        matches = re.findall(pattern, llm_response, re.DOTALL)
        params = [match.strip() for match in matches][0]
        params = json.loads(params)
        return self.format_params(params)
    
    def format_params(self, params):
        params = {k:v/100 if "rate" in k.lower() or "share" in k.lower() else v for k, v in params.items()}
        return params

    def invoke(self, **kwargs):
        exp_params = super().invoke(**kwargs)
        created_data = create_data(**exp_params)
        return {'data' : created_data, 'params':exp_params}


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from openai import AzureOpenAI

    load_dotenv(override=True)
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

    client = AzureOpenAI(
                api_key=AZURE_OPENAI_API_KEY,
                api_version=AZURE_OPENAI_API_VERSION,
                azure_endpoint=AZURE_OPENAI_ENDPOINT
            )

    agent = ExperimentAgent(client=client)

    out = agent.invoke(question="What would be the drop in sales if the LOE happened in 2029")

    print(out)

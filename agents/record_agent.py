import sys
sys.path.append("D:/pfizer_demo")
from agents.base_agent import BaseAgent
from agents.prompts import RecordPrompt
from utils import create_data
import re
import json

class RecordAgent(BaseAgent):
    
    def __init__(self, client, prompt=RecordPrompt, model=None):
        if model is None:
            super().__init__(prompt=prompt, client=client)
        else:
            super().__init__(prompt=prompt, client=client, model=model)
        self.params_formatted=False

    def extract_output(self, llm_response):
        # print(llm_response)
        pattern = r"```json(.*?)```"
        matches = re.findall(pattern, llm_response, re.DOTALL)
        try:
            versions = [match.strip() for match in matches][-1]
            # print("LLM RESPONSE", llm_response)
            # print("JSON",versions)
            versions = json.loads(versions)
            param_sets = {k:v for k, v in versions.items() if k != 'comparison_requested'}
            versions_extracted = self.fetch_versions(param_sets)
            versions_extracted['comparison_requested'] = versions['comparison_requested']
            return versions_extracted
        
        except:
            print("trying again")
            # print("LLM RESPONSE", llm_response)
            return self.invoke(**self.invoke_args)

        

    def fetch_versions(self, sets):
        true = TRUE = True
        false = FALSE = False

        out = {}
        for set_id in sets:
            out[set_id] = [j['version'] for j in sets[set_id] if j['is_correct'].lower() == "true"]
        
        return out
    
    def build_conversation_history(self, history):
        history_output = []
        for record in history:
            record_data = record['data']
            if not self.params_formatted:
                record_params = self.format_params(record['params'])
                self.params_formatted=True
            else:
                record_params = record['params']
                
            record_version = record['version']

            temp_output = f"""VERSION : {record_version}
- Parmeters: {record_params}
- Data: {record_data}"""

            history_output.append(temp_output)
    
        history_output = "\n\n".join(history_output)
        # print(history_output)
        return history_output
    

    def format_prompt(self, **kwargs):
        kwargs['experiment_history'] = self.build_conversation_history(kwargs['experiment_history'])
        return self.prompt.format(**kwargs)


    def format_params(self, params):
        params = {k:f"{v*100}%" if "rate" in k.lower() or "share" in k.lower() else v for k, v in params.items()}
        return params


    def invoke(self, **kwargs):
        self.invoke_args = kwargs
        llm_output = super().invoke(**kwargs)
        # print(self.format_prompt(**kwargs))
        return llm_output


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from openai import AzureOpenAI
    import pandas as pd

    load_dotenv(override=True)
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

    data_path = "D:\\pfizer_demo\\experiments\\data"
    param_path = "D:\\pfizer_demo\\experiments\\params"

    client = AzureOpenAI(
                api_key=AZURE_OPENAI_API_KEY,
                api_version=AZURE_OPENAI_API_VERSION,
                azure_endpoint=AZURE_OPENAI_ENDPOINT
            )

    agent = RecordAgent(client=client)
    
    experiment_history = []

    for data_file, params_file in zip(os.listdir(data_path), os.listdir(param_path)):
        try:
            data = pd.read_csv(os.path.join(data_path,data_file))
        except:
            continue
        
        try:
            with open(os.path.join(param_path, params_file), 'r', encoding = "utf-8") as f:
                params = json.load(f)
        except:
            continue

        version = data_file.split("_")[-1].split(".")[0]

        experiment_history.append({"data":data.to_markdown(), "params":str(params), "version":version})


    question = "Compare the previous version with the base version"
    out = agent.invoke(question=question, experiment_history=experiment_history)
    
    print(out)

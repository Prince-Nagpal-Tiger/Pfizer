import sys
sys.path.append("D:/pfizer_demo")
from agents.base_agent import BaseAgent
from agents.prompts import IntentPrompt
import re
import json

class IntentAgent(BaseAgent):

    def __init__(self, client, prompt=IntentPrompt, model=None):
        if model is None:
            super().__init__(prompt=prompt, client=client)
        else:
            super().__init__(prompt=prompt, client=client, model=model)


    def extract_output(self, llm_response):
        pattern = r"```json(.*?)```"
        matches = re.findall(pattern, llm_response, re.DOTALL)
        out = [match.strip() for match in matches][0]
        out = json.loads(out)
        return out
    
    def format_params(self, params):
        params = {k:f'{v*100}%' if "rate" in k.lower() or "share" in k.lower() else v for k, v in params.items()}
        return params
    
    def invoke(self, **kwargs):
        kwargs['params'] = str(self.format_params(kwargs['params']))
        llm_output = super().invoke(**kwargs)

        return llm_output


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

    agent = IntentAgent(client=client)

    questions = """What happens to Drug A after LOE in 2037?
    What is the projected revenue in 2040?
    What % of the population is diagnosed in 2040?
    What happens if a competitor enters before 2037?
    What happens if a biosimilar launches in 2036 instead of 2037?
    What price discount will generic competitors offer?
    Can Drug A retain a strong market presence post-LOE?
    How can Drug A delay LOE impact?
    Can a new indication offset LOE losses?
    What is the expected price decline post-LOE?
    How are market events changed in this cycle as compared to previous cycle for therapeutic area A?
    What is the deviation in the outputs?
    Did region US deviate from the guidance significantly to create their scenarios?
    Did the current scenario deviate significantly from the previous experiment?
    Generate data for a scenario where the Market share decay post loe is 30%
    What is the impact on price when competitor enters the market in 2032""".split("\n")


    for question in questions:
        print(question)
        print(agent.invoke(question=question, year="2037"))
        print("****")
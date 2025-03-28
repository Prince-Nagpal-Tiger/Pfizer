import sys
sys.path.append("D:/pfizer_demo")
from agents.base_agent import BaseAgent
from agents.prompts import ComparePrompt


class CompareAgent(BaseAgent):

    def __init__(self, client, prompt=ComparePrompt, model=None):
        if model is None:
            super().__init__(prompt=prompt, client=client)
        else:
            super().__init__(prompt=prompt, client=client, model=model)

    def extract_output(self, llm_output):
        return llm_output.split("SUMMARY:")[-1]
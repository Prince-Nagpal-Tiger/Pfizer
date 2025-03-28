import sys
sys.path.append("D:/pfizer_demo")
from agents.base_agent import BaseAgent
from agents.prompts import QueryPrompt


class QueryAgent(BaseAgent):

    def __init__(self, client, prompt=QueryPrompt, model=None):
        if model is None:
            super().__init__(prompt=prompt, client=client)
        else:
            super().__init__(prompt=prompt, client=client, model=model)
        self.params_formatted=False


    def format_params(self, params):
        params = {k:f"{v*100}%" if "rate" in k.lower() or "share" in k.lower() else v for k, v in params.items()}
        return params

    def extract_output(self, llm_output):
        marker = "SUMMARY:"
        try:
            return llm_output.split(marker)[-1].strip()
        except:
            print("Trying Again")
            return self.invoke(**self.invoke_args)
        # return llm_output


    def invoke(self, **kwargs):
        # print("Prompt:", self.format_prompt(**kwargs))
        if not self.params_formatted:
            kwargs['params'] = str(self.format_params(kwargs['params']))
        # print("Prompt:", self.format_prompt(**kwargs))
        self.invoke_args = kwargs
        self.params_formatted = True
        # print(kwargs)
        # print(kwargs)
        llm_output = super().invoke(**kwargs)
        # print(llm_output)
        return llm_output
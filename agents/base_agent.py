class BaseAgent:

    def __init__(self, client, prompt, model='pfz-gpt-4o'):
        self.client = client
        self.prompt = prompt
        self.model = model

    def format_prompt(self, **kwargs):
        return self.prompt.format(**kwargs)

    
    def extract_output(self, llm_response):
        return llm_response

    def invoke(self, **kwargs):
        llm_input = self.format_prompt(**kwargs)
        client = self.client

        response = client.chat.completions.create(model=self.model,
        messages=[
            {"role": "system", "content": "You follow the instructions that are given to you."},
            {"role": "user", "content": llm_input}
            ],)

        llm_output = response.choices[0].message.content

        extracted_response = self.extract_output(llm_output)

        return extracted_response
    
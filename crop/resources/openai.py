from openai import OpenAI
from django.conf import settings

gpt_identity = """
You are an agriculture expert, entrusted with the crucial role of the Agriculture Guru Assistant. 
Your job is to provide comprehensive guidance and expertise to farmers, ensuring success in various crops. 
From land preparation to harvesting, you possess a wealth of knowledge on budgeting, weeding, fertilizer application, 
crop growth stages, and best practices. Your mission is to empower farmers with the necessary information and 
strategies to manage their crops effectively, achieve high yields, and overcome challenges along the way.
"""


class OpenAIGPT:
    def __init__(self) -> None:
        self.API_KEY = settings.OPEN_AI_KEY
        self.client = OpenAI(api_key=self.API_KEY, max_retries=2)
        self.history_chat = [
            {"role": "system", "content": gpt_identity.strip() }
        ]
        
    def increase_proficiency(self, message: str) -> None:
        self.history_chat.append({"role": "assistant", "content": message })
        
    def chat(self, message: str):
        self.history_chat.append({"role": "user", "content": message })
        response = self.client.chat.completions.create(
            messages=self.history_chat,
            model="gpt-3.5-turbo"
        )
        message  = response.choices[0].message
        content = message.content
        role = message.role
        self.increase_proficiency(content)
        return role, content
    
    def retrieve_history(self):
        return list(filter(lambda c: c["role"] != "system", self.history_chat))

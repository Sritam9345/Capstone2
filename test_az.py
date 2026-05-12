from openai import AzureOpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from enum import Enum

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-08-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

class sentiment(str, Enum):
    positive = "positive"
    negative = "negative"


class Answer(BaseModel):
    answer: sentiment



response = client.beta.chat.completions.parse(
    model="gpt-4.1-nano",
    messages=[
        {
            "role": "system",
            "content": "Extract structured information."
        },
        {
            "role": "user",
            "content": "I absolutely loved the movie."
        }
    ],
    response_format=Answer
)

result = response.choices[0].message.parsed


print(result)
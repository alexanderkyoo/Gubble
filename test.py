import openai
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are estimating the usage lifespan of items."},
        {"role": "user", "content": "How many days would you predict that it would take someone to run out of the following. Give an exact number of days, and only a single number, no extra text." + "toilet paper"}
    ]
)
print(completion.choices[0].message.content)

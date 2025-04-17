from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# configure Azure OpenAI service client 
client = AzureOpenAI(
  azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"], 
  api_key=os.environ['AZURE_OPENAI_API_KEY'],  
  api_version = "2023-10-01-preview"
  )

deployment=os.environ['AZURE_OPENAI_DEPLOYMENT']

programming_language = input("What programming language do you want to learn?: ")

lesson_level = input("What level of lesson do you want to learn? (beginner, intermediate, advanced): ")

prompt = f"""Suggest a {lesson_level} lesson for {programming_language} in the following format:
    - concepts:
    - brief explanation of the lesson:
    - exercise in code with solutions"""
messages = [{"role": "user", "content": prompt}]

completion = client.chat.completions.create(model=deployment, messages=messages, max_tokens=400, temperature = 0.1)


# print response
print("Plan:")
print(completion.choices[0].message.content)

# old_prompt_result = completion.choices[0].message.content
# prompt_shopping = "Produce a shopping list, and please don't include ingredients that I already have at home: "

# new_prompt = f"Given ingredients at home {ingredients} and these generated recipes: {old_prompt_result}, {prompt_shopping}"
# messages = [{"role": "user", "content": new_prompt}]
# completion = client.chat.completions.create(model=deployment, messages=messages, max_tokens=600, temperature=0)

# print response
# print("\n=====Shopping list ======= \n")
# print(completion.choices[0].message.content)

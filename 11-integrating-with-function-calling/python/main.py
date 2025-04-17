import requests
import json

from openai import AzureOpenAI
import os
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# configure Azure OpenAI service client 
client = AzureOpenAI(
  azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"], 
  api_key=os.environ['AZURE_OPENAI_API_KEY'],  
  api_version = "2023-10-01-preview"
  )


deployment=os.environ['AZURE_OPENAI_DEPLOYMENT']

def search_courses(role, product, level):
    url = "https://learn.microsoft.com/api/catalog/"
    params = {
        "role": role,
        "product": product,
        "level": level
    }
    
    response = requests.get(url, params=params)
    modules = response.json()["modules"]
    results = []
    
    for module in modules[:5]:
        title = module["title"]
        url = module["url"]
        results.append({"title": title, "url": url})
    
    return str(results)


messages = [
    {
        "role": "user",
        "content": "Find me a good course for a beginner student to learn Azure."
    }
]

functions = [
    {
        "name": "search_courses",
        "description": "Retrieves courses from the search index based on the parameters provided",
        "parameters": {
            "type": "object",
            "properties": {
                "role": {
                    "type": "string",
                    "description": "The role of the learner (i.e. developer, data scientist, student, etc.)"
                },
                "product": {
                    "type": "string",
                    "description": "The product that the lesson is covering (i.e. Azure, Power BI, etc.)"
                },
                "level": {
                    "type": "string",
                    "description": "The level of experience the learner has prior to taking the course (i.e. beginner, intermediate, advanced)"
                }
            },
            "required": ["role"]
        }
    }
]

response = client.chat.completions.create(
    model=deployment,
    messages=messages,
    functions=functions,
    function_call="auto"
)

print(response.choices[0].message)
response_message = response.choices[0].message

# Check if the model wants to call a function
if response_message.function_call.name:
    print("Recommended Function call:")
    print(response_message.function_call.name)
    print()

    # Call the function
    function_name = response_message.function_call.name
    available_functions = {
        "search_courses": search_courses,
    }
    function_to_call = available_functions[function_name]

    function_args = json.loads(response_message.function_call.arguments)
    function_response = function_to_call(**function_args)

    print("Output of function call:")
    print(function_response)
    print(type(function_response))

    # Add the assistant response and function response to the messages
    messages.append(  # adding assistant response to messages
        {
            "role": response_message.role,
            "function_call": {
                "name": function_name,
                "arguments": response_message.function_call.arguments,
            },
            "content": None
        }
    )
    
    messages.append(  # adding function response to messages
        {
            "role": "function",
            "name": function_name,
            "content": function_response,
        }
    )

    print("Messages in next request:")
    print(messages)
    print()

    second_response = client.chat.completions.create(
        messages=messages,
        model=deployment,
        function_call="auto",
        functions=functions,
        temperature=0
    )

    print(second_response.choices[0].message)

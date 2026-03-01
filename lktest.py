import openai, json
import requests

client = openai.OpenAI()
messages = []



def get_popular_movies(): #- /movies에서 인기 영화를 가져옵니다.
    response = requests.get("https://nomad-movies.nomadcoders.workers.dev/movies")
    return response.json()

def get_movie_details(id): # - /movies/:id에서 영화 정보를 가져옵니다.
    response = requests.get("https://nomad-movies.nomadcoders.workers.dev/movies/{id}")
    return response.json()
    
def get_movie_credits(id): # - /movies/:id/credits에서 출연진 및 제작진을 가져옵니다.
    
    response = requests.get("https://nomad-movies.nomadcoders.workers.dev/movies/{id}/credits")
    return response.json()

def get_similar_movies(id): # - /movies/:id/similar 에서 유사한 영화를 조회합니다. 
    response = requests.get("https://nomad-movies.nomadcoders.workers.dev/movies/{id}/similar")
    return response.json()
    


FUNCTION_MAP = {
    "get_popular_movies": get_popular_movies,
    "get_movie_details": get_movie_details,
    "get_movie_credits": get_movie_credits, 
    "get_similar_movies": get_similar_movies, 
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_popular_movies",
            "description": "A function to get the list of popular movies.",
            "parameters": {
                "type": "object",
                "properties":{},
            }
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_movie_details",
            "description": "A function to get the movie details with the specific id of a popular movie.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The id of the movie."
                    }
                }
            },
            "required": ["id"]
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_movie_credits",
            "description": "A function to get the credits for a movie.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The id of the movie."
                    }
                }
            },
            "required": ["id"]
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_similar_movies",
            "description": "A function to get similar movies for a movie.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "The id of the movie."
                    }
                }
            },
            "required": ["id"]
        },
    },
       
]

from openai.types.chat import ChatCompletionMessage

def process_ai_response(message: ChatCompletionMessage):

    if message.tool_calls:
        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in message.tool_calls
                ],
            }
        )

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = tool_call.function.arguments

            print(f"Calling function: {function_name} with {arguments}")

            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {}

            function_to_run = FUNCTION_MAP.get(function_name)

            result = function_to_run(**arguments)

            print(f"Ran {function_name} with args {arguments} for a result of {result}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": result,
                }
            )

        call_ai()
    else:
        messages.append({"role": "assistant", "content": message.content})
        print(f"AI: {message.content}")


def call_ai():
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
    )
    process_ai_response(response.choices[0].message)   


while True:
    message = input("Send a message to the LLM: ")
    if message == "quit" or message == "q" :
        break
    else:
        messages.append({"role": "user", "content": message})
        print(f"User: {message}")
        call_ai()
    
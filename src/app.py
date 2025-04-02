import chainlit as cl


from openai import AzureOpenAI
import os

# may change in the future
# https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#rest-api-versioning
api_version = os.environ.get("azure_openai_api_version")
azure_endpoint = os.environ.get("azure_openai_endpoint", "")
deployment_name = os.environ.get("azure_openai_deployment")
llm_model = os.environ.get("azure_openai_model", "")
azure_api_key = os.environ.get("azure_openai_key", "")

client = AzureOpenAI(
    api_version=api_version, azure_endpoint=azure_endpoint, azure_deployment=deployment_name, api_key=azure_api_key
)


def create_user_message(content: str):
    return {
        "role": "user",
        "content": content,
    }


@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...
    #
    messages = [create_user_message(message.content)]

    completion = client.chat.completions.create(
        model="model",
        messages=messages,  # type: ignore
    )

    response = completion.choices[-1].message.content

    await cl.Message(
        content=response or "",
    ).send()

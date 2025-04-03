import chainlit as cl

from mcp_client import MCPClient

from loguru import logger

conversation_messages = []


def create_user_message(content: str):
    return {
        "role": "user",
        "content": content,
    }


client = MCPClient()


@cl.on_chat_start
async def on_chat_start():
    logger.info("A new chat session has started!")
    try:
        await client.connect_to_server()
    except Exception as e:
        print(e)


@cl.on_message
async def main(message: cl.Message):
    # add message received from chainlit to the history
    formated_message = create_user_message(message.content)
    conversation_messages.append(formated_message)

    response_message = await client.get_completion(conversation_messages)


    # add message to cl interface
    await cl.Message(
        content=response_message.content or "Error getting response from API",
    ).send()

    # add response to history
    conversation_messages.append(response_message)


@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")

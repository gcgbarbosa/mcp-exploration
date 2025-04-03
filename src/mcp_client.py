import asyncio
from typing import Any, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

from loguru import logger
import json
import os
from openai import AzureOpenAI
from openai.types.chat import ChatCompletionMessage

api_version = os.environ.get("azure_openai_api_version")
azure_endpoint = os.environ.get("azure_openai_endpoint", "")
deployment_name = os.environ.get("azure_openai_deployment")
llm_model = os.environ.get("azure_openai_model", "")
azure_api_key = os.environ.get("azure_openai_key", "")


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools_openai_format = []
        self.client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=azure_endpoint,
            azure_deployment=deployment_name,
            api_key=azure_api_key,
        )

    async def connect_to_server(self, server_script_path: str = "src/mcp_server.py"):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """

        command = "python"
        server_params = StdioServerParameters(command=command, args=[server_script_path], env=None)

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))

        self.stdio, self.write = stdio_transport

        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools

        logger.debug(f"Connected to server with tools: {[tool.name for tool in tools]}")

        self.tools_openai_format = [self.from_mcp_tool_to_openai(tool) for tool in tools]

    def from_mcp_tool_to_openai(self, tool: types.Tool):
        parameters = tool.inputSchema

        parameters["additionalProperties"] = False

        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": (tool.description or "").strip(),
                "parameters": parameters,
                "strict": True,
            },
        }

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

    async def get_completion(self, messages: list[dict[str, Any] | ChatCompletionMessage]):
        if not self.session:
            raise ValueError("Session is not initialized. Call connect_to_server() first.")

        # get response from api
        completion = self.client.chat.completions.create(
            model="model",
            messages=messages,  # type: ignore
            tools=self.tools_openai_format,  # type: ignore
        )

        response = completion.choices[-1]

        if response.finish_reason == "tool_calls":
            # call tool
            tool_calls = response.message.tool_calls

            if not tool_calls:
                raise ValueError("No tool calls found in the response")

            messages.append(response.message)

            # TODO: do it for all calls

            tool_call = tool_calls[-1]

            function = tool_call.function

            arguments: dict[str, Any] = json.loads(function.arguments)

            func_response = await self.session.call_tool(function.name, arguments)

            logger.debug(f"Tool call result: {func_response}")

            text_output = (
                "[" + ";".join([r.text for r in func_response.content if isinstance(r, types.TextContent)]) + "]"
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function.name,
                    "content": text_output,
                }
            )

            # get response from api
            completion = self.client.chat.completions.create(
                model="model",
                messages=messages,  # type: ignore
                tools=self.tools_openai_format,  # type: ignore
            )

            response = completion.choices[-1]

            return response.message

        logger.debug(f"Received response: {completion}")

        # process response
        return response.message


async def main():
    client = MCPClient()
    try:
        await client.connect_to_server()
        # await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

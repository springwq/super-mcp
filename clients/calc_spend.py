import asyncio
import json
import sys
from datetime import datetime, timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain.schema import HumanMessage, AIMessage

from langchain_aws import ChatBedrock
from dotenv import load_dotenv

load_dotenv()

python_path = sys.executable

model = ChatBedrock(
    region="us-west-2",
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    model_kwargs=dict(temperature=0),
    beta_use_converse_api=True,
    verbose=True,
)

async def main():
    print("Starting the application...")
    async with MultiServerMCPClient() as client:
        print("Connecting to Jampp server...")
        await client.connect_to_server(
            "jampp",
            command=python_path,
            args=["servers/jampp_mcp_server.py"],
            encoding_error_handler="ignore",
        )

        print("Connecting to spend_rate server...")
        await client.connect_to_server(
            "spend_rate",
            command=python_path,
            args=["servers/spend_rate.py"],
            encoding_error_handler="ignore",
        )

        print("Creating agent...")
        agent = create_react_agent(model, client.get_tools(), debug=True)

        print("Available tools:", [tool.name for tool in client.get_tools()])
        print("Sending query to agent...")
        review_requested = await agent.ainvoke(debug=True, input={
            "messages": "返回 2025-03 月份的 campaign spend 数据，找到 2025-03-01 的 campaign spend 数据"
        })

        print("Processing response...")
        parsed_data = parse_ai_messages(review_requested)
        for ai_message in parsed_data:
            print(ai_message)
        print("Finished")

def parse_ai_messages(data):
    messages = dict(data).get('messages', [])
    formatted_ai_responses = []

    for message in messages:
        if isinstance(message, AIMessage):
            formatted_message = f"### AI Response:\n\n{message.content}\n\n"
            formatted_ai_responses.append(formatted_message)

    return formatted_ai_responses

if __name__ == "__main__":
    asyncio.run(main())

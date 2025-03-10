import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from langchain_aws import ChatBedrock
from dotenv import load_dotenv

load_dotenv()

async def run():
    model = ChatBedrock(
        region="us-west-2",
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_kwargs=dict(temperature=0),
        beta_use_converse_api=True,
        verbose=True,
    )

    server_params = StdioServerParameters(
        command = "python",
        args = ["./servers/spend_rate.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()


            tools = await load_mcp_tools(session)

            agent = create_react_agent(model, tools)
            agent_response = await agent.ainvoke(
                {
                    "messages": """
                    现有 first_purchase = 4, date = 2025-03-01, click_url_id = 20660
                    已知 gross_spend = first_purchase * gross_rate, net_spend = first_purchase * net_rate
                    请问 gross_spend 和 net_spend 值是多少?
                    """
                }
            )
            for m in agent_response["messages"]:
                m.pretty_print()


asyncio.run(run())

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

async def setup_servers(client):
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

    print("Connecting to timeserver...")
    await client.connect_to_server(
        "timeserver",
        command=python_path,
        args=["-m", "mcp_simple_timeserver"],
        encoding_error_handler="ignore",
    )

def has_valid_data(results):
    """检查结果是否包含有效的数据"""
    if not results:
        return False

    for result in results:
        # 检查是否包含"没有数据"、"数据为空"等表示无数据的关键词
        no_data_keywords = ["没有数据", "数据为空", "无数据", "empty", "no data"]
        if any(keyword in result.lower() for keyword in no_data_keywords):
            return False
        # 检查是否包含具体的数字或金额
        if any(char.isdigit() for char in result):
            return True
    return False

def modify_query(original_query, attempt):
    """根据尝试次数修改查询"""
    if "2025" in original_query:  # 如果查询包含未来日期，改为当前年份
        return original_query.replace("2025", "2024")

    if attempt == 1:
        # 扩大日期范围到前后3天
        return original_query + " 请查询目标日期前后3天的数据"
    elif attempt == 2:
        # 尝试获取最近7天的数据
        return "请查询最近7天的 campaign spend 数据，并按支出金额排序"
    elif attempt == 3:
        # 尝试获取当月的汇总数据
        return "请查询本月的 campaign spend 汇总数据，找出支出最高的 campaign"
    else:
        # 尝试获取可用的最新数据
        return "请查询最新可用的 campaign spend 数据，并显示支出最高的 campaign"

async def process_query(agent, query):
    try:
        review_requested = await agent.ainvoke(debug=True, input={
            "messages": query
        })
        return parse_ai_messages(review_requested)
    except Exception as e:
        return [f"### Error:\n\n发生错误: {str(e)}\n\n"]

async def execute_query_with_retry(agent, original_query, max_attempts=4):
    """执行查询，如果没有有效数据则自动重试"""
    current_query = original_query
    results = None

    for attempt in range(max_attempts):
        print(f"\n尝试 {attempt + 1}/{max_attempts}")
        print(f"当前查询: {current_query}")

        results = await process_query(agent, current_query)
        print("\n查询结果:")
        for result in results:
            print(result)

        if has_valid_data(results):
            print("\n✓ 已获取到有效数据")
            return results

        print("\n! 未获取到有效数据，正在调整查询...")
        current_query = modify_query(original_query, attempt + 1)

    return results

def validate_results(results):
    """验证返回的结果是否满足需求"""
    if not results:
        return False, "没有返回任何结果"

    # 检查结果中是否包含关键信息
    for result in results:
        if "campaign" in result.lower() and "spend" in result.lower():
            return True, "结果包含了 campaign 和 spend 信息"

    return False, "结果缺少必要的 campaign 或 spend 信息"

async def main():
    print("Starting the application...")

    async with MultiServerMCPClient() as client:
        print("Setting up servers...")
        await setup_servers(client)

        print("Creating agent...")
        agent = create_react_agent(model, client.get_tools(), debug=True)

        available_tools = client.get_tools()
        print("\nAvailable tools:", [tool.name for tool in available_tools])

        if not available_tools:
            print("警告：没有可用的工具，请检查服务器连接")
            return

        while True:
            try:
                print("\n请输入您的查询 (输入 'exit' 退出):")
                user_input = input().strip()

                if user_input.lower() == 'exit':
                    break

                if not user_input:
                    print("查询不能为空，请重新输入")
                    continue

                print("\n开始处理查询...")
                results = await execute_query_with_retry(agent, user_input)

                # 验证最终结果
                is_valid, message = validate_results(results)
                print(f"\n最终结果验证: {message}")

                if not is_valid:
                    print("\n虽然进行了多次尝试，但仍未能获得理想的结果。")
                    print("建议：")
                    print("1. 检查数据是否存在于系统中")
                    print("2. 确认查询的时间范围是否合理")
                    print("3. 尝试使用不同的查询方式")

                print("\n是否继续新的查询? (y/n):")
                if input().strip().lower() != 'y':
                    break

            except Exception as e:
                print(f"\n发生错误: {str(e)}")
                print("请重试或输入 'exit' 退出")

def parse_ai_messages(data):
    messages = dict(data).get('messages', [])
    formatted_ai_responses = []

    for message in messages:
        if isinstance(message, AIMessage):
            formatted_message = f"### AI Response:\n\n{message.content}\n\n"
            formatted_ai_responses.append(formatted_message)

    return formatted_ai_responses

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n程序发生错误: {str(e)}")
    finally:
        print("\n程序已退出")

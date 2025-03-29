from pathlib import Path

import logfire
from nonebot_plugin_alconna import UniMessage
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP, MCPServerStdio

from .config import plugin_config

# 仅用于在[logfire](logfire.pydantic.dev)上追踪模型的调用过程
logfire.configure(send_to_logfire="if-token-present")

logfire.instrument_pydantic_ai()


def get_mcp_servers() -> list[MCPServerHTTP | MCPServerStdio]:
    """获取MCP服务器列表"""
    mcp_servers = []
    if plugin_config.enable_example_mcp_server:
        example_server_dir = Path(__file__).parent / "example_servers"
        server_path = example_server_dir / "e2b_mcp_server.py"
        mcp_servers.append(
            MCPServerStdio(
                command="uv",
                args=["run", str(server_path)],
                env={"E2B_API_KEY": plugin_config.e2b_api_key},
            )
        )
    if plugin_config.mcp_servers:
        for server in plugin_config.mcp_servers:
            mcp_servers.append(MCPServerHTTP(url=server))
    return mcp_servers


async def run(
    user_id: str | None = None,
    group_id: str | None = None,
    message: str | None = None,
    model: str | None = None,
) -> UniMessage:
    if not model:
        model = plugin_config.mcp_default_model

    mcp_servers = get_mcp_servers()

    agent = Agent(
        model=model,
        mcp_servers=mcp_servers,
        retries=5,
    )

    async with agent.run_mcp_servers():
        response = await agent.run(message)
        return response.data

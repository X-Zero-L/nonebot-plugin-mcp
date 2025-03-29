import time

import logfire
from nonebot_plugin_alconna import UniMessage
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP, MCPServerStdio
from pydantic_ai.messages import ModelMessage

from .config import plugin_config

# 仅用于在[logfire](logfire.pydantic.dev)上追踪模型的调用过程
logfire.configure(send_to_logfire="if-token-present")

logfire.instrument_pydantic_ai()


def get_mcp_servers() -> list[MCPServerHTTP | MCPServerStdio]:
    """获取MCP服务器列表"""
    mcp_servers = []
    if plugin_config.enable_example_mcp_server:
        mcp_servers.append(
            MCPServerStdio(
                command="npx",
                args=["-y", "@pydantic/mcp-run-python", "stdio"],
            )
        )
    if plugin_config.mcp_servers:
        for server in plugin_config.mcp_servers:
            mcp_servers.append(MCPServerHTTP(url=server))
    return mcp_servers


class UserHistory(BaseModel):
    """用户历史记录模型"""

    user_id: str
    messages: list[ModelMessage] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)

    class Config:
        arbitrary_types_allowed = True


user_history: dict[str, UserHistory] = {}


def get_user_history(user_id: str) -> UserHistory:
    """获取或创建用户历史记录"""
    if user_id not in user_history or (user_history[user_id].timestamp + 600 < time.time()):
        user_history[user_id] = UserHistory(user_id=user_id)
    return user_history[user_id]


def set_user_history(user_id: str, messages: list[ModelMessage]):
    """设置用户历史记录"""
    if user_id not in user_history:
        user_history[user_id] = UserHistory(user_id=user_id)
    user_history[user_id].messages = messages
    user_history[user_id].timestamp = time.time()


async def run(
    user_id: str,
    group_id: str | None = None,
    message: str | None = None,
    model: str | None = None,
    no_history: bool = False,
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
        response = await agent.run(
            message, message_history=get_user_history(user_id).messages if not no_history else None
        )
        set_user_history(user_id, response.all_messages()) if not no_history else None
        return response.data

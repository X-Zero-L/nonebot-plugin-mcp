from nonebot import get_driver, get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    mcp_default_model: str = "openai:gpt-4o"  # agent使用的默认模型
    enable_example_mcp_server: bool = (
        True  # 是否启用示例MCP服务器（通过本地子进程运行）,目前为一个需要npx安装的run-python-mcp
    )
    mcp_servers: list[str] = []  # MCP服务器列表，默认全启用
    allowed_models: list[str] = ["openai:gpt-4o"]  # 允许的模型列表


# 配置加载
plugin_config: Config = get_plugin_config(Config)
global_config = get_driver().config

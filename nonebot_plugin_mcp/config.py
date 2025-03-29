from nonebot import get_driver, get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    mcp_default_model: str = "openai:gpt-4o"  # agent使用的默认模型


# 配置加载
plugin_config: Config = get_plugin_config(Config)
global_config = get_driver().config

# 全局名称
NICKNAME: str | None = next(iter(global_config.nickname), None)

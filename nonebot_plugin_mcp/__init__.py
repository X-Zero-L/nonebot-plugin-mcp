from nonebot import logger, require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_waiter")
require("nonebot_plugin_uninfo")
require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")
require("nonebot_plugin_apscheduler")
from nonebot_plugin_uninfo import Session, Uninfo, UniSession

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="Nonebot MCP",
    description="描述",
    usage="用法",
    type="application",  # library
    homepage="https://github.com/X-Zero-L/nonebot-plugin-mcp",
    config=Config,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna", "nonebot_plugin_uninfo"),
    extra={"author": "X-Zero-L <zeroeeau@gmail.com>"},
)

from arclet.alconna import Alconna, Args, Arparma, Option, Subcommand
from nonebot_plugin_alconna import Match, MsgId, on_alconna
from nonebot_plugin_alconna.uniseg import UniMessage

from . import core

# 无上下文的单任务模式，适合只需要单次交互的场景
single_task = on_alconna(
    Alconna(
        "/mcp_single",
        Args["prompt", str],
        Option("--model|-m|--model_name", Args["model", str], default="openai:gpt-4o", help_text="指定模型"),
    ),
    use_cmd_start=True,
    priority=5,
    block=True,
    aliases={"/mcps", "mcp_single", "mcps"},
)
allow_model = [
    "openai:gpt-4o",
]


@single_task.handle()
async def handle_single_task(prompt: Match[str], model: Match[str], msg_id: MsgId, session: Uninfo):
    if model.result not in allow_model:
        logger.warning(f"不支持的模型：{model.result}")
        await single_task.finish("不支持的模型，请使用以下模型之一：\n" + "\n".join(allow_model))
    user_id = session.user.id
    await single_task.finish(await core.run(user_id=user_id, message=prompt.result, model=model.result, single=True))

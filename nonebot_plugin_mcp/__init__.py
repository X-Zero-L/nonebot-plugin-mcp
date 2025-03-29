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
from nonebot_plugin_alconna import AlconnaMatcher, Match, MsgId, on_alconna
from nonebot_plugin_alconna.uniseg import UniMessage

from . import core

# 定义允许的模型列表
ALLOWED_MODELS = [
    "openai:gpt-4o",
]

# 无上下文的单任务模式，适合只需要单次交互的场景
no_history_task = on_alconna(
    Alconna(
        "/mcp_no_history",
        Args["prompt", str],
        Option("--model|-m|--model_name", Args["model", str], default="openai:gpt-4o", help_text="指定模型"),
    ),
    use_cmd_start=True,
    priority=5,
    block=True,
    aliases={"mcps", "mcp_no_history"},
)

# 带上下文
task = on_alconna(
    Alconna(
        "/mcp",
        Args["prompt", str],
        Option("--model|-m|--model_name", Args["model", str], default="openai:gpt-4o", help_text="指定模型"),
    ),
    use_cmd_start=True,
    priority=5,
    block=True,
    aliases={"mcp"},
)


async def process_task(matcher: AlconnaMatcher, prompt: str, model: str, user_id: str, no_history: bool = False):
    if model not in ALLOWED_MODELS:
        logger.warning(f"不支持的模型：{model}")
        await matcher.finish("不支持的模型，请使用以下模型之一：\n" + "\n".join(ALLOWED_MODELS))

    result = await core.run(user_id=user_id, message=prompt, model=model, no_history=no_history)
    await matcher.finish(result)


@no_history_task.handle()
async def handle_no_history_task(prompt: Match[str], model: Match[str], session: Uninfo):
    await process_task(no_history_task, prompt.result, model.result, session.user.id, no_history=True)


@task.handle()
async def handle_task(prompt: Match[str], model: Match[str], session: Uninfo):
    await process_task(task, prompt.result, model.result, session.user.id)

from collections.abc import Sequence
import json
import logging
from typing import Any

from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox
from mcp.server import Server
from mcp.types import (
    EmbeddedResource,
    ImageContent,
    TextContent,
    Tool,
)
from pydantic import BaseModel, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("e2b-mcp-server")
load_dotenv()


# Tool schema
class ToolSchema(BaseModel):
    code: str


app = Server("e2b-code-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="run_code",
            description="Run python code in a secure sandbox by E2B. Using the Jupyter Notebook syntax.",
            inputSchema=ToolSchema.model_json_schema(),
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls."""
    if name != "run_code":
        raise ValueError(f"Unknown tool: {name}")

    try:
        arguments = ToolSchema.model_validate(arguments)
    except ValidationError as e:
        raise ValueError(f"Invalid code arguments: {e}") from e

    sbx = Sandbox()
    execution = sbx.run_code(arguments.code)
    logger.info(f"Execution: {execution}")

    result = {
        "results": [str(x) for x in execution.results],
        "stdout": execution.logs.stdout,
        "stderr": execution.logs.stderr,
    }
    text = json.dumps(result, indent=2)
    logger.info(f"Result: {text}")
    return [TextContent(type="text", text=text)]


async def main():
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

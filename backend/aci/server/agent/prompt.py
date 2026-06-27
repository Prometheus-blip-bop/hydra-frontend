# mypy: ignore-errors
import json

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from aci.common.logging_setup import get_logger
from aci.common.schemas.function import OpenAIResponsesFunctionDefinition
from aci.server import config

from .types import ClientMessage

logger = get_logger(__name__)


def convert_to_openai_messages(messages: list[ClientMessage]) -> list[ChatCompletionMessageParam]:
    """
    Convert a list of ClientMessage objects to a list of OpenAI messages.

    Args:
        messages: A list of ClientMessage objects

    Returns:
        A list of OpenAI messages
    """
    openai_messages = []

    for message in messages:
        if message.tool_invocations:
            # Convert ToolInvocation objects to dictionaries before adding them
            for ti in message.tool_invocations:
                openai_messages.append(
                    {
                        "type": "function_call",
                        "call_id": ti.tool_call_id,
                        "name": ti.tool_name,
                        "arguments": json.dumps(ti.args),
                    }
                )
                if ti.result:
                    openai_messages.append(
                        {
                            "type": "function_call_output",
                            "call_id": ti.tool_call_id,
                            "output": json.dumps(ti.result),
                        }
                    )
            continue
        else:
            content = []
            content.append(
                {
                    "type": "input_text" if message.role == "user" else "output_text",
                    "text": message.content,
                }
            )
            openai_messages.append({"role": message.role, "type": "message", "content": content})

    return openai_messages


async def openai_chat_stream(
    messages: list[ChatCompletionMessageParam],
    tools: list[OpenAIResponsesFunctionDefinition],
):
    """
    Stream chat completion responses and handle tool calls asynchronously.
    """
    client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.LLM_BASE_URL)

    # Convert tools to standard OpenAI chat completion tools format
    standard_tools = [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            }
        }
        for t in tools
    ] if tools else None

    try:
        kwargs = {
            "model": config.LLM_MODEL,
            "messages": messages,
            "stream": True,
        }
        if standard_tools:
            kwargs["tools"] = standard_tools

        stream = client.chat.completions.create(**kwargs)
        
        tool_call_states = {}
        
        for chunk in stream:
            if not chunk.choices:
                continue
                
            delta = chunk.choices[0].delta
            
            # Stream text content
            if delta.content:
                yield f"0:{json.dumps(delta.content)}\n"
                
            # Handle tool calls streaming
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    index = tc.index
                    if index not in tool_call_states:
                        tool_call_states[index] = {
                            "id": tc.id,
                            "name": tc.function.name if tc.function else "",
                            "arguments": tc.function.arguments if tc.function and tc.function.arguments else ""
                        }
                    else:
                        if tc.function and tc.function.arguments:
                            tool_call_states[index]["arguments"] += tc.function.arguments
                            
            finish_reason = chunk.choices[0].finish_reason
            if finish_reason:
                if finish_reason == "tool_calls":
                    for index, tc_state in tool_call_states.items():
                        args_str = tc_state["arguments"] if tc_state["arguments"] else "{}"
                        yield f'9:{{"toolCallId":"{tc_state["id"]}","toolName":"{tc_state["name"]}","args":{args_str}}}\n'
                
                yield 'd:{"finishReason":"' + finish_reason + '"}\n'

    except Exception as e:
        logger.exception("Error during LLM stream")
        error_message = f"LLM Error: {str(e)}"
        yield f"0:{json.dumps(error_message)}\n"

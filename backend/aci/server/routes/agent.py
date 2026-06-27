from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel

from aci.common.enums import FunctionDefinitionFormat
from aci.common.logging_setup import get_logger
from aci.common.schemas.function import OpenAIResponsesFunctionDefinition
from aci.server import config
from aci.server import dependencies as deps
from aci.server.agent.prompt import (
    ClientMessage,
    convert_to_openai_messages,
    openai_chat_stream,
)
from aci.server.routes.functions import get_functions_definitions

router = APIRouter()
logger = get_logger(__name__)
openai_client = OpenAI(api_key=config.OPENAI_API_KEY)


class AgentChat(BaseModel):
    id: str
    linked_account_owner_id: str
    selected_apps: list[str]
    selected_functions: list[str]
    messages: list[ClientMessage]


@router.post(
    "/chat",
    response_class=StreamingResponse,
    summary="Chat with AI agent",
    description="Handle chat requests and stream responses with tool calling capabilities",
    response_description="Streamed chat completion responses",
)
async def handle_chat(
    context: Annotated[deps.RequestContext, Depends(deps.get_request_context)],
    agent_chat: AgentChat,
) -> StreamingResponse:
    """
    Handle chat requests and stream responses.

    Args:
        context: Request context with authentication and project info
        agent_chat: Chat request containing messages and function information

    Returns:
        StreamingResponse: Streamed chat completion responses
    """

    openai_messages = convert_to_openai_messages(agent_chat.messages)
    # TODO: support different meta function mode.
    selected_functions = await get_functions_definitions(
        context.db_session, agent_chat.selected_functions, FunctionDefinitionFormat.OPENAI_RESPONSES
    )

    tools = [
        func for func in selected_functions if isinstance(func, OpenAIResponsesFunctionDefinition)
    ]

    project = context.project
    llm_api_key = project.llm_api_key
    llm_base_url = project.llm_base_url
    llm_model = project.llm_model
    
    if not llm_api_key:
        if project.message_count >= 10:
            async def error_stream():
                yield '0:"Free tier exhausted! Please visit Project Settings to provide your own LLM API Key."\n'
            
            response = StreamingResponse(error_stream())
            response.headers["x-vercel-ai-data-stream"] = "v1"
            return response
            
        project.message_count += 1
        context.db_session.flush()
        context.db_session.commit()

    response = StreamingResponse(
        openai_chat_stream(
            openai_messages, 
            tools=tools,
            api_key=llm_api_key,
            base_url=llm_base_url,
            model=llm_model
        )
    )
    response.headers["x-vercel-ai-data-stream"] = "v1"

    return response

import logging
from typing import Any, TypeVar

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import get_settings
from app.services import security

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def get_chat_model() -> ChatOpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not set — copy .env.example to .env and add your key."
        )
    return ChatOpenAI(
        model=settings.openai_model, api_key=settings.openai_api_key, temperature=0
    )


def generate_structured(
    system_prompt: str, data_payload: dict[str, Any], output_schema: type[T]
) -> T:

    model = get_chat_model().with_structured_output(
        output_schema, method="function_calling"
    )
    messages = [
        ("system", system_prompt),
        ("human", security.wrap_untrusted_data(data_payload)),
    ]
    logger.info(
        "calling %s for %s", get_settings().openai_model, output_schema.__name__
    )
    return model.invoke(messages)

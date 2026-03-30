import logging

from langchain_core.messages import HumanMessage, SystemMessage

from gpt_computer.core.token_usage import TokenUsageLog


def test_usage_cost_non_openai(caplog):
    # Tests that non-openai models return None and log a message
    token_usage_log = TokenUsageLog("gemini-1.5-pro")
    request_messages = [
        SystemMessage(content="my system message"),
        HumanMessage(content="my user prompt"),
    ]
    response = "response from model"

    token_usage_log.update_log(request_messages, response, "step 1")

    with caplog.at_level(logging.INFO):
        cost = token_usage_log.usage_cost()

    assert cost is None
    assert (
        "Cost calculation for model gemini-1.5-pro is not fully supported yet"
        in caplog.text
    )


def test_image_tokenizer_low_detail():
    from gpt_computer.core.token_usage import Tokenizer

    tokenizer = Tokenizer("gpt-4")
    cost = tokenizer.num_tokens_for_base64_image(
        "invalid_base64_but_doesnt_matter", detail="low"
    )
    assert cost == 85

import os
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.openai import OpenAIModel
from strands_tools import file_read, editor, shell


load_dotenv()

model = OpenAIModel(
    client_args={
        "api_key": os.environ["TOKEN_HARBOR_API_KEY"],
        "base_url": "https://tokenharbor.ai/v1",  # from their docs
    },
    model_id="deepseek-v4.1-flash:free",  # or "mimo-v2.6-flash:free"
)


@tool
def read_file(path: str) -> str:
    """Read a file and return its contents."""
    with open(path, encoding="utf-8") as f:
        return f.read()


model2 = OpenAIModel(
    client_args={
        "api_key": os.environ["TOKEN_HARBOR_API_KEY"],
        "base_url": "https://tokenharbor.ai/v1",  # from their docs
    },
    model_id="mimo-v2.6-flash:free",  # or "mimo-v2.6-flash:free"
)

agent = Agent(model=model, tools=[read_file])
agent("in the first law universe, is it ever revealed what the bloody nine is?")

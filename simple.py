import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from strands import Agent, AgentSkills, tool
from strands.models.openai import OpenAIModel
from strands_tools import file_read, editor, shell
from pydantic import BaseModel
from strands.hooks import BeforeToolCallEvent, HookProvider, HookRegistry


load_dotenv()

model = OpenAIModel(
    client_args={
        "api_key": os.environ["TOKEN_HARBOR_API_KEY"],
        "base_url": "https://tokenharbor.ai/v1",  # from their docs
    },
    model_id="deepseek-v4.1-flash:free",  # or "mimo-v2.6-flash:free"
)



model2 = OpenAIModel(
    client_args={
        "api_key": os.environ["TOKEN_HARBOR_API_KEY"],
        "base_url": "https://tokenharbor.ai/v1",  # from their docs
    },
    model_id="mimo-v2.6-flash:free",  # or "mimo-v2.6-flash:free"
)
@tool
def calculator(a: float, b: float, operation: str = "add") -> str:
    """Perform a math operation on two numbers.

    Args:
        a: First number
        b: Second number
        operation: One of "add", "subtract", "multiply", "divide", "power"
    """
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        result = a / b if b != 0 else "Error: division by zero"
    elif operation == "power":
        result = a ** b
    else:
        result = f"Unknown operation: {operation}"
    return str(result)

def buffered_handler(**kwargs):
    # Only show complete messages, not individual streaming chunks
    if "message" in kwargs and kwargs["message"].get("role") == "assistant":
        content = kwargs["message"].get("content", [])
        for block in content:
            if "text" in block:
                print(block["text"])

@tool
def verify_answer(question: str, answer: str) -> str:
    """Have an independent reviewer check an answer before it is given to the user.

    Args:
        question: The user's original question.
        answer: The proposed answer, including the calculation steps.
    """
    verifier = Agent(
        model=model2,
        tools=[calculator],
        callback_handler=None,  # keep the verifier's output out of the terminal
        system_prompt=(
            "You are a strict reviewer. Recalculate the answer independently "
            "using the calculator tool. Reply with exactly 'VERIFIED' if it is "
            "correct, or 'WRONG: <reason and correct answer>' if not."
        ),
    )
    return str(verifier(f"Question: {question}\nProposed answer: {answer}"))

    

app = FastAPI()


class PromptRequest(BaseModel):
    prompt: str


@app.post("/stream")
async def stream_response(request: PromptRequest):
    async def generate():
        agent = Agent(model=model, tools=[calculator, verify_answer], plugins=[skills_plugin], callback_handler=None)
        async for event in agent.stream_async(request.prompt):
            if "data" in event:
                yield event["data"]

    return StreamingResponse(generate(), media_type="text/plain")

class DeleteApprovalHook(HookProvider):
    """Intercepts delete operations for human approval."""

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeToolCallEvent, self.check_delete)

    def check_delete(self, event: BeforeToolCallEvent) -> None:
        if event.tool_use["name"] != "delete_file":
            return

        approval = event.interrupt(
            "delete-approval",
            reason={"path": event.tool_use["input"]["path"]}
        )

        if approval.lower() != "y":
            event.cancel_tool = "User denied file deletion"

skills_plugin = AgentSkills(skills="./skills")

if __name__ == "__main__":
    agent = Agent(
        model=model, 
        tools=[calculator, verify_answer], 
        callback_handler=buffered_handler,
        hooks=[DeleteApprovalHook()],
        plugins=[skills_plugin]
    )
    
    agent("What is 2 to the power of 16, minus 1?")

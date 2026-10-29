import asyncio

import pandas as pd

from anthropic          import AsyncAnthropic
from concurrent.futures import ThreadPoolExecutor
from datetime           import datetime
from pathlib            import Path

pd.set_option("display.max_colwidth", 80)

from src.agent.src.tools      import init

from src.agent      import set_model, get_model, load_Agent
from src.agent      import Agent, Supervisor
from src.agent      import execute, get_context

from src.agent.src.tools      import list_id

from src.api import launch_api
from src.api import Request

init()

set_model("qwen3:4b", AsyncAnthropic(base_url="http://localhost:11434", api_key="ollama"))

__DATA = Path("data")
__MODEL = __DATA / "model"

WEB_AGENT = __MODEL / "web_agent.joblib"
DB_AGENT = __MODEL / "db_agent.joblib"

SUPERVISER = __MODEL / "supervisor_agent.joblib"

assistant_web = load_Agent(WEB_AGENT)
assistant_db = load_Agent(DB_AGENT)

WORKERS = {"assistant web": assistant_web, "assistant data": assistant_db}
SUPERVISEUR = get_context("superviser")

supervisor = Supervisor("superviseur", SUPERVISEUR, agents=WORKERS)

def ask(agent, request: str, sender: str):

    async def inner_ask(agent: str, request: str):
        run = await execute(agent, request, max_token=8192, USER = sender, TODAY = str(datetime.now()))
        return run
        
    with ThreadPoolExecutor(max_workers=1) as ex:
        result= ex.submit(asyncio.run, inner_ask(agent=agent, request=request)).result()
        return result


def displayer(request: Request) :
    print(request.user.username, "sent the message\"", request.message, "\"")
    reply = ask(agent=supervisor, request=request.message, sender = request.user.username)
    return {"reply": reply.reponse}

app = launch_api(displayer)
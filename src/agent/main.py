import asyncio

import pandas as pd

from anthropic          import AsyncAnthropic
from concurrent.futures import ThreadPoolExecutor
from IPython.display    import Markdown, display
from pathlib            import Path

pd.set_option("display.max_colwidth", 80)

from src.trace      import test_span
from src.trace      import afficher_trace
from src.tools      import init

from src.agent      import set_model, get_model, load_Agent
from src.agent      import Agent, Supervisor
from src.agent      import execute, get_context

from src.tools      import list_id

set_model("qwen3:4b", AsyncAnthropic(base_url="http://localhost:11434", api_key="ollama"))  #"claude-haiku-4-5-20251001"

__DATA = Path("data")
__MODEL = __DATA / "model"

WEB_AGENT = __MODEL / "web_agent.joblib"
DB_AGENT = __MODEL / "db_agent.joblib"

SUPERVISER = __MODEL / "supervisor_agent.joblib"

init()

assistant_web = load_Agent(WEB_AGENT)
assistant_db = load_Agent(DB_AGENT)

WORKERS = {"assistant web": assistant_web, "assistant data": assistant_db}
SUPERVISEUR = get_context("superviser")

supervisor = Supervisor("superviseur", SUPERVISEUR, agents=WORKERS)

def ask(agent: Agent, request: str):

    async def inner_ask(agent: str, request: str):
        run = await execute(agent, request, max_token=8192)
        afficher_trace(run.trace_id)
        display(Markdown(run.reponse))
        return run
        
    with ThreadPoolExecutor(max_workers=1) as ex:
        result= ex.submit(asyncio.run, inner_ask(agent=agent, request=request)).result()
        return result

run = ask(supervisor, "Ajoute l'utilisateur Arthur Magnin, né le 10 Aout, étant un étudiant en informatique à l'EPITA.")
print("-" * 50)
print(run.reponse)
print("\n")
print(list_id())

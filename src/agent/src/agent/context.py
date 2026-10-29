from pathlib import Path

__DATA = Path("data")
__CONTEXT = __DATA / "context"

def get_context(agent: str) :
    try :
        f = open(__CONTEXT / f"{agent}_context.txt")
        return f.read()
    except Exception as e :
        raise ValueError(f"No context detected for the agent {agent}")

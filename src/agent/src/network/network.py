from ..agent import load_Agent, Supervisor, executer
from pathlib import Path

class Network:
    def __init__(self, max_token: int):
        self.max_token: int = max_token
        data = Path("src/agent/data")
        agents = data / "model"

        self.supervisor: Supervisor = load_Agent(agents / "supervisor_agent.joblib")

    def ask(self, question: str, display: bool = False) -> str :
        executer(self.supervisor, question, max_token=self.max_token, display=display)
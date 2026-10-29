from src.api import launch_api
from src.api import Request

def displayer(request: Request) :
    print(request.user.username, "sent the message\"", request.message, "\"")
    return {"reply": "Message well received"}

app = launch_api(displayer)
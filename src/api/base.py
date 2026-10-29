from .schema import Request
from fastapi import FastAPI

def launch_api(handle_request) :
    app = FastAPI()

    @app.get("/")
    def read_root():
        return {"message": "HelloWorld!"}

    @app.post("/ask/")
    def read_item(request: Request):
        if (not request.message) :
            raise ValueError("The request is missing the message field.")
        return handle_request(request)

    return app
from pydantic import BaseModel

from .user import User

class Request(BaseModel) :
    user        : User  = None
    timestamp   : str   = None
    message     : str   = None
from pydantic import BaseModel,Field
from enum import Enum
from typing import Dict,Optional


class userSchema(BaseModel):
    name: str
    passowrd: str


class Role(str,Enum):
    
    user = "user"
    ai = "ai"

class chatSchema(BaseModel):
    name: str
    message: list[Dict[Role,str]]
    threadID: str
    

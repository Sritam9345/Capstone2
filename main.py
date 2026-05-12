from fastapi import FastAPI
from service.main import checkUniqueUser,answerUserQuery
from pydantic import BaseModel
import json

app = FastAPI()

class userQueryModel(BaseModel):
    username: str
    userQuery: str
    threadID: str


@app.get('/')
def home():
    return {'message':'Hi there its Sritam'}



@app.get('/signup')
def checkUser(username: str):
    try:
        checkUniqueUser(username=username)
        print("user created successfully!")
    except Exception as e:
        raise(e)
    


@app.post('/answer')
def userAnswer(data: userQueryModel):

    result = answerUserQuery(userInput=data.userQuery , username=data.username,threadID=data.threadID)
    
    return{"ai message":result}
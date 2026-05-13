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



@app.post('/signup')
def checkUser(data: dict):
    try:
        response = checkUniqueUser(username=data['username'])

        userData = {}
        messagesToCorrespondingThread = {}

        for results in response:
            
            if 'name' not in userData.keys():
                userData['name'] = results['name']

            if 'threadID' not in userData.keys():
                userData['threadID'] = [results['threadID']]
            else:
                userData['threadID'].append(results['threadID'])

            messagesToCorrespondingThread[results['threadID']] = results['message']

        print({
            'userData': userData,
            'messages': messagesToCorrespondingThread
        })
        
        return {
            'userData': userData,
            'messages': messagesToCorrespondingThread
        }

    except Exception as e:
        raise(e)
@app.post('/answer')
def userAnswer(data: userQueryModel):

    result = answerUserQuery(userInput=data.userQuery , username=data.username,threadID=data.threadID)
    
    return{"ai message":result}
from fastapi import FastAPI,UploadFile,File,Form
from service.main import checkUniqueUser,answerUserQuery
from pydantic import BaseModel
import json
from blob_upload.main import uploadFile
from fastapi.responses import JSONResponse

app = FastAPI()

class userQueryModel(BaseModel):
    username: str
    userQuery: str
    threadID: str


@app.get('/')
def home():
    return {'message':'Hi there its Sritam'}



@app.post('/signup')
async def checkUser(data: dict):
    try:
        response = await checkUniqueUser(username=data['username'])

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
async def userAnswer(data: userQueryModel):

    result = await answerUserQuery(userInput=data.userQuery , username=data.username,threadID=data.threadID)
    
    return {"ai message":result}


@app.post('/upload-file')
async def handleFile(file: UploadFile = File(...)):
    try:
        response = await uploadFile(file.file,file.filename)
        return {'message': response}
    except Exception as e:
        return str(e)    
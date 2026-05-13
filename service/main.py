from graph_logic.graph import userConversation
from db.main import collection_chat
from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse


def checkUniqueUser(username):
    exists = collection_chat.find({"name": username})
    
    return exists

def answerUserQuery(userInput,username,threadID):
    result = userConversation(userInput=userInput , username=username,threadID=threadID)
    return result

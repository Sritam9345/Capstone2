from graph_logic.graph import userConversation
from db.main import collection_chat
from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse


async def checkUniqueUser(username):
    response = await collection_chat.find({"name": username}).to_list(length=None)
    
    return response

async def answerUserQuery(userInput,username,threadID):
    result = await userConversation(userInput=userInput , username=username,threadID=threadID)
    return result

# def ingest():
    
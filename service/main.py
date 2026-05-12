from graph_logic.graph import userConversation
from db.main import collection_chat





def checkUniqueUser(username):
    exists = collection_chat.find_one({"username": username})

    if exists:
        raise Exception("Username already exists...")
    
    collection_chat.insert_one({
        "username": username
    })

    return True

def answerUserQuery(userInput,username,threadID):
    result = userConversation(userInput=userInput , username=username,threadID=threadID)
    return result
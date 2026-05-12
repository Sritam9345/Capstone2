from typing import TypedDict, Annotated, List
from langgraph.graph import START, StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage
from queryRetrieve.main import context_retrieval
from llm.main import model
from pydantic import BaseModel,Field
from enum import Enum
from langgraph.checkpoint.memory import InMemorySaver
from db.main import collection_chat

memory = InMemorySaver()

class askToImprove(str,Enum):
    yes = 'yes'
    no = 'no'

class ChatState(TypedDict):
    user: Annotated[List[BaseMessage], add_messages]
    ai: Annotated[List[BaseMessage], add_messages]
    max_iterations: int
    current_iteration: int
    context: dict[int,str]
    agent: str
    validatorRoute: str
    improve: askToImprove


def retriever(state: ChatState):

    userMessage = state["user"][-1].content

    result = context_retrieval(userMessage)

    for i in range(0, len(result['id'])):

        if result['id'][i] not in state['context'].keys():

            state['context'][result['id'][i]] = result['doc'][i]

    return {
        "context": state["context"]
    }

class Role(str, Enum):
    knowledgeBasedAgent = "knowledgeBasedAgent"
    technicalSupportAgent = "technicalSupportAgent"
    complianceAgent = "complianceAgent"

class PlannerSchema(BaseModel):
    agent: Role

class validationSchema(BaseModel):
    score: float = Field(ge=0, le=1)


def plannerAgent(state: ChatState):

    userMessage = state["user"][-1].content

    response = model.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": """
You are a planner agent.

Available agents:
- knowledgeBasedAgent
- technicalSupportAgent
- complianceAgent

Return the best agent for the task.
"""
            },
            {
                "role": "user",
                "content": userMessage
            }
        ],
        response_format=PlannerSchema
    )

    result = response.choices[0].message.parsed

    return {
        "agent": result.agent
    }
    
    
def knowledgeBasedAgent(state: ChatState):

    contextChunks = state.get("context", {})

    contextText = "\n\n".join(
        f"Chunk ID: {chunkId}\nText: {chunkText}"
        for chunkId, chunkText in contextChunks.items()
    )

    improve = state.get("improve", "no")

    conversationHistory = []

    maxHistory = min(len(state["user"]), len(state["ai"]))

    for i in range(maxHistory):

        conversationHistory.append({
            "role": "user",
            "content": state["user"][i].content
        })

        conversationHistory.append({
            "role": "assistant",
            "content": state["ai"][i].content
        })

    if len(state["user"]) > len(state["ai"]):
        latestUserMessage = state["user"][-1]

        conversationHistory.append({
            "role": "user",
            "content": latestUserMessage.content
        })
    
    print(conversationHistory)
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are a knowledge based agent. "
                "Answer only using the provided context. "
                "If the context is insufficient, say so clearly."
            ),
        },
        *conversationHistory,
        {
            "role": "user",
            "content": f"""
Retrieved Context:
{contextText}

AskedToImprove:
{improve}
"""
        }
    ]

    response = model.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages,
    )

    aiContent = response.choices[0].message.content

    if improve == "yes" and state["ai"]:

        latestAiMessage = state["ai"][-1]

        return {
            "ai": [
                AIMessage(
                    content=aiContent,
                    id=latestAiMessage.id
                )
            ]
        }

    return {
        "ai": [AIMessage(content=aiContent)]
    }
    
    
def technicalSupportAgent(state: ChatState):

    contextChunks = state.get("context", {})

    contextText = "\n\n".join(
        f"Chunk ID: {chunkId}\nText: {chunkText}"
        for chunkId, chunkText in contextChunks.items()
    )

    improve = state.get("improve", "no")

    conversationHistory = []

    maxHistory = min(len(state["user"]), len(state["ai"]))

    for i in range(maxHistory):

        conversationHistory.append({
            "role": "user",
            "content": state["user"][i].content
        })

        conversationHistory.append({
            "role": "assistant",
            "content": state["ai"][i].content
        })

    if len(state["user"]) > len(state["ai"]):

        latestUserMessage = state["user"][-1]

        conversationHistory.append({
            "role": "user",
            "content": latestUserMessage.content
        })

    messages = [
        {
            "role": "system",
            "content": (
                "You are a technical support agent. "
                "Provide technical troubleshooting and debugging help "
                "using the provided context."
            ),
        },
        *conversationHistory,
        {
            "role": "user",
            "content": f"""
Retrieved Context:
{contextText}

AskedToImprove:
{improve}
"""
        }
    ]

    response = model.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages,
    )

    aiContent = response.choices[0].message.content

    if improve == "yes" and state["ai"]:

        latestAiMessage = state["ai"][-1]

        return {
            "ai": [
                AIMessage(
                    content=aiContent,
                    id=latestAiMessage.id
                )
            ]
        }

    return {
        "ai": [AIMessage(content=aiContent)]
    }


def complianceAgent(state: ChatState):

    contextChunks = state.get("context", {})

    contextText = "\n\n".join(
        f"Chunk ID: {chunkId}\nText: {chunkText}"
        for chunkId, chunkText in contextChunks.items()
    )

    improve = state.get("improve", "no")

    conversationHistory = []

    maxHistory = min(len(state["user"]), len(state["ai"]))

    for i in range(maxHistory):

        conversationHistory.append({
            "role": "user",
            "content": state["user"][i].content
        })

        conversationHistory.append({
            "role": "assistant",
            "content": state["ai"][i].content
        })

    if len(state["user"]) > len(state["ai"]):

        latestUserMessage = state["user"][-1]

        conversationHistory.append({
            "role": "user",
            "content": latestUserMessage.content
        })

    messages = [
        {
            "role": "system",
            "content": (
                "You are a compliance agent. "
                "Ensure the response follows company policies, "
                "regulations, compliance requirements, and safety guidelines."
            ),
        },
        *conversationHistory,
        {
            "role": "user",
            "content": f"""
Retrieved Context:
{contextText}

AskedToImprove:
{improve}
"""
        }
    ]

    response = model.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages,
    )

    aiContent = response.choices[0].message.content

    if improve == "yes" and state["ai"]:

        latestAiMessage = state["ai"][-1]

        return {
            "ai": [
                AIMessage(
                    content=aiContent,
                    id=latestAiMessage.id
                )
            ]
        }

    return {
        "ai": [AIMessage(content=aiContent)]
    }


def validatorAgent(state: ChatState):

    currentIteration = state["current_iteration"]
    maxIterations = state["max_iterations"]

    if currentIteration >= maxIterations:
        return {
            "current_iteration": currentIteration,
            "validationRoute": "beautifyAgent"
        }

    latestAnswer = state["ai"][-1].content
    userMessage = state["user"][-1].content

    response = model.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": """
You are a validator agent.

Score the answer from 0 to 1 based on:
- correctness
- relevance
- completeness
- usefulness

Return only the score.
"""
            },
            {
                "role": "user",
                "content": f"""
User Query:
{userMessage}

Specialized Agent Answer:
{latestAnswer}
"""
            }
        ],
        response_format=validationSchema
    )

    result = response.choices[0].message.parsed

    if result.score > 0.5:
        return {
            "current_iteration": currentIteration,
            "validationRoute": "beautifyAgent"
        }

    return {
        "current_iteration": currentIteration+1,
        "validationRoute": state["agent"],
        'improve':'yes'
    }
    
    
    
def beautifyAgent(state: ChatState):

    latestAnswer = state["ai"][-1].content
    userMessage = state["user"][-1].content

    response = model.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a beautify agent. "
                    "Improve the clarity, readability, structure, "
                    "grammar, and presentation of the response "
                    "without changing its meaning."
                ),
            },
            {
                "role": "user",
                "content": f"""
User Query:
{userMessage}

Current Answer:
{latestAnswer}
""",
            },
        ],
    )

    beautifiedContent = response.choices[0].message.content

    latestAiMessage = state["ai"][-1]

    return {
        "ai": [
            AIMessage(
                content=beautifiedContent,
                id=latestAiMessage.id
            )
        ]
    }
    
    


graph = StateGraph(ChatState)
    

graph.add_node('plannerAgent',plannerAgent)
graph.add_node('retriever',retriever)
graph.add_node('knowledgeBasedAgent',knowledgeBasedAgent)
graph.add_node('technicalSupportAgent',technicalSupportAgent)
graph.add_node('complianceAgent',complianceAgent)
graph.add_node('validatorAgent',validatorAgent)
graph.add_node('beautifyAgent',beautifyAgent)


graph.add_edge(START, "retriever")
graph.add_edge("retriever", "plannerAgent")

graph.add_conditional_edges(
    "plannerAgent",
    lambda state: state["agent"],
    {
        "knowledgeBasedAgent": "knowledgeBasedAgent",
        "technicalSupportAgent": "technicalSupportAgent",
        "complianceAgent": "complianceAgent",
    }
)

graph.add_edge("knowledgeBasedAgent", "validatorAgent")
graph.add_edge("technicalSupportAgent", "validatorAgent")
graph.add_edge("complianceAgent", "validatorAgent")

graph.add_conditional_edges(
    "validatorAgent",
    lambda state: state["validationRoute"],
    {
        "knowledgeBasedAgent": "knowledgeBasedAgent",
        "technicalSupportAgent": "technicalSupportAgent",
        "complianceAgent": "complianceAgent",
        "beautifyAgent": "beautifyAgent",
    }
)

graph.add_edge("beautifyAgent", END)

finalGraph = graph.compile()


from uuid import uuid4


threadId = str(uuid4())

config = {
    "configurable": {
        "thread_id": threadId
    }
}






def userConversation(userInput, username, threadID):

    chatDoc = collection_chat.find_one({
        "name": username,
        "threadID": threadID
    })

    userMessages = []
    aiMessages = []

    
    
    if chatDoc and "message" in chatDoc:

        for message in chatDoc["message"]:

            role = message.get("role")
            content = message.get("content", "")

            if role == "user":
                userMessages.append(
                    HumanMessage(content=content)
                )

            elif role == "ai":
                aiMessages.append(
                    AIMessage(content=content)
                )

    userMessages.append(
        HumanMessage(content=userInput)
    )

    
    
    
    result = finalGraph.invoke(
        {
            "user": userMessages,
            "ai": aiMessages,

            "max_iterations": 3,

            "current_iteration": 0,

            "context": {},

            "agent": "",

            "validatorRoute": "",

            "improve": "no"
        }
    )

    aiMessage = result["ai"][-1].content

    updatedMessages = []

    totalHistory = min(
        len(userMessages),
        len(aiMessages)
    )

    for i in range(totalHistory):

        updatedMessages.append({
            "role": "user",
            "content": userMessages[i].content
        })

        updatedMessages.append({
            "role": "ai",
            "content": aiMessages[i].content
        })

    updatedMessages.append({
        "role": "user",
        "content": userInput
    })

    updatedMessages.append({
        "role": "ai",
        "content": aiMessage
    })

    collection_chat.update_one(
        {
            "name": username,
            "threadID": threadID
        },
        {
            "$set": {
                "name": username,
                "threadID": threadID,
                "message": updatedMessages
            }
        },
        upsert=True
    )

    return aiMessage

from typing import TypedDict, Annotated, List
from langgraph.graph import START, StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage
# from queryRetrieve.main import context_retrieval
from llm.main import model
from pydantic import BaseModel,Field
from enum import Enum
from db.main import collection_chat,redis
import json
import asyncio
import aiohttp

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
    summary: str


async def retriever(state: ChatState):

    query = state["user"][-1].content
    
    async with aiohttp.ClientSession() as session:
        async with session.post('http://api:8051/retrieve',data=query) as response:
            result = await response.json()
            
            for i in result:
                state['context'][i] = result[i]
    return {
        "context":state['context']
    }

class Role(str, Enum):
    knowledgeBasedAgent = "knowledgeBasedAgent"
    technicalSupportAgent = "technicalSupportAgent"
    complianceAgent = "complianceAgent"

class PlannerSchema(BaseModel):
    agent: Role

class validationSchema(BaseModel):
    score: float = Field(ge=0, le=1)


async def plannerAgent(state: ChatState):

    userMessage = state["user"][-1].content

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
        ]
    
    
    response = await llmInvoke(messages=messages,schema=PlannerSchema)

    result = response.choices[0].message.parsed

    return {
        "agent": result.agent
    }
    
    
async def knowledgeBasedAgent(state: ChatState):

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
""",
            "summary":state['summary']
        }
    ]

    response = await llmInvoke(messages=messages)

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
    
    
async def technicalSupportAgent(state: ChatState):

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
""",
            "summary":state['summary']
        }
    ]

    response = await llmInvoke(messages=messages)

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


async def complianceAgent(state: ChatState):

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
""",
            "summary":state['summary']
        }
    ]

    response = await llmInvoke(messages=messages)

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


async def validatorAgent(state: ChatState):

    currentIteration = state["current_iteration"]
    maxIterations = state["max_iterations"]

    if currentIteration >= maxIterations:
        return {
            "current_iteration": currentIteration,
            "validationRoute": "beautifyAgent"
        }

    latestAnswer = state["ai"][-1].content
    userMessage = state["user"][-1].content

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
""",
            "summary":state['summary']
            }
        ]
    
        
    
    
    response = await llmInvoke(messages=messages,schema=validationSchema)

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
    
    
    
async def beautifyAgent(state: ChatState):

    latestAnswer = state["ai"][-1].content
    userMessage = state["user"][-1].content

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
            "summary":state['summary']
            },
        ]
    
    
    response = await llmInvoke(messages=messages)
    
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

async def userConversation(username,userInput,threadID):
    
    flattenedUserKey = f"{username}:{threadID}"
    
    cachedResult = await redis.get(flattenedUserKey)
     
    result = {}
     
    if not cachedResult:
        print('cache miss')
        userChat = await collection_chat.find_one({
            'name':username,
            'threadID':threadID
        })

        
        if not userChat:
            result = await cacheMissAndUserNotPresent(
                userInput=userInput,  
                )
        else:
            result = await cacheMissButUserPresent(
                userInput=userInput,
                userData=userChat
            )
    
    else:
        print('cache hit')
        cache = json.loads(cachedResult)
        result = await cacheHit(
            cache=cache,
            userInput=userInput
        )

    dataOnRedis = {}
    
    if cachedResult:
        dataOnRedis = json.loads(cachedResult)
        dataOnRedis['message'].extend([{'role':'user','content':userInput},{'role':'ai','content':result['answer']}])
    else:
        dataOnRedis['message']=[]
        dataOnRedis['message'].extend([{'role':'user','content':userInput},{'role':'ai','content':result['answer']}])
        dataOnRedis['summary'] = result['summary']
    
    await redis.set(flattenedUserKey,json.dumps(dataOnRedis))
    
    return result['answer']
  
async def cacheMissAndUserNotPresent(userInput):
    
    userMessage=[]
    aiMessage = []
    
    userMessage.append(HumanMessage(content=userInput))
    
    result = await finalGraph.ainvoke(
        {
            "user": userMessage,
            "ai": aiMessage,

            "max_iterations": 3,

            "current_iteration": 0,

            "context": {},

            "agent": "",

            "validatorRoute": "",

            "improve": "no",
            
            "summary": ""
        }
    )
    
    answer = result['ai'][-1].content
    summary = ""
    
    
    
    return {
        "answer":answer,
        "summary": summary
    }

async def cacheMissButUserPresent(userInput,userData):
    
    userMessage = []
    aiMessage = []
    
    messages = [
    {
        "role": "system",
        "content": "Generate a concise summary of the conversation along with personal details in 250 words."
    }
]

    for item in userData["message"]:
        if item["role"] == 'ai':
            messages.append({
                "role": 'assistant',
                "content": item["content"]
            })
        else:
            messages.append({
                "role": 'user',
                "content": item["content"]
            })
        
        if item["role"] == 'user':
            userMessage.append(HumanMessage(content=item['content']))
        else:
            aiMessage.append(AIMessage(content=item['content']))
    
    
    userMessage.append(HumanMessage(content=userInput))
    
    result = await llmInvoke(messages=messages)

    summary = result.choices[0].message.content
    
    result = await finalGraph.ainvoke(
        {
            "user": userMessage,
            "ai": aiMessage,

            "max_iterations": 3,

            "current_iteration": 0,

            "context": {},

            "agent": "",

            "validatorRoute": "",

            "improve": "no",
            
            "summary": summary
        }
    )
    
    answer = result['ai'][-1].content
    
    
    return {
        'answer':answer,
        'summary':summary
    }
    
async def cacheHit(userInput,cache):
    userMessage = []
    aiMessage = []
    
    for item in cache['message']:
        if item['role'] =='user':
            userMessage.append(HumanMessage(content=item['content']))
        else:
            aiMessage.append(AIMessage(content=item['content']))
    
    summary = cache['summary']
    
    userMessage.append(HumanMessage(content=userInput))
    
    result = await finalGraph.ainvoke(
        {
            "user": userMessage,
            "ai": aiMessage,

            "max_iterations": 3,

            "current_iteration": 0,

            "context": {},

            "agent": "",

            "validatorRoute": "",

            "improve": "no",
            
            "summary": summary
        }
    )
    
    answer = result['ai'][-1].content
    
    return {
        'answer':answer,
        'summary':summary
    }
    
async def llmInvoke(messages,schema=None):
    
    if schema:
        response = await model.beta.chat.completions.parse(
            model="gpt-4.1-nano",
            messages=messages,
            response_format=schema
        )
    else:
        response = await model.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages
        )
    return response
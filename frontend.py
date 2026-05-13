import requests
import streamlit as st
from uuid import uuid4

API_BASE_URL = "http://localhost:8000"


if "loginState" not in st.session_state:
    st.session_state.loginState = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "threads" not in st.session_state:
    st.session_state.threads = []

if "activeThreadId" not in st.session_state:
    st.session_state.activeThreadId = ""

if "threadMessages" not in st.session_state:
    st.session_state.threadMessages = {}


def ensure_thread_exists():
    if not st.session_state.activeThreadId:
        new_thread_id = str(uuid4())
        st.session_state.threads.append(new_thread_id)
        st.session_state.threadMessages[new_thread_id] = []
        st.session_state.activeThreadId = new_thread_id

    if st.session_state.activeThreadId not in st.session_state.threadMessages:
        st.session_state.threadMessages[st.session_state.activeThreadId] = []


def login(username: str):
    response = requests.post(
        f"{API_BASE_URL}/signup",
        json={"username": username},
        timeout=15,
    )

    result = response.json()
    print(result)

    if response.status_code != 200:
        st.error("Login failed")
        return

    st.session_state.loginState = True

    userData = result.get("userData", {})
    messages = result.get("messages", {})

    # New user
    if userData == {} and messages == {}:
        st.session_state.username = username
        st.session_state.threads = []
        st.session_state.threadMessages = {}
        st.session_state.activeThreadId = ""
        ensure_thread_exists()
        return

    # Existing user
    st.session_state.username = userData.get("name", username)
    st.session_state.threads = userData.get("threadID", [])

    st.session_state.threadMessages = {}

    for threadID in st.session_state.threads:
        st.session_state.threadMessages[threadID] = messages.get(threadID, [])

    if st.session_state.threads:
        st.session_state.activeThreadId = st.session_state.threads[0]
    else:
        st.session_state.activeThreadId = ""
        ensure_thread_exists()


def sendQuery(userInput: str):
    ensure_thread_exists()

    threadID = st.session_state.activeThreadId

    st.session_state.threadMessages[threadID].append({
        "role": "user",
        "content": userInput
    })

    response = requests.post(
        f"{API_BASE_URL}/answer",
        json={
            "username": st.session_state.username,
            "threadID": threadID,
            "userQuery": userInput
        },
        timeout=30,
    )

    result = response.json()

    if response.status_code != 200:
        st.session_state.threadMessages[threadID].append({
            "role": "ai",
            "content": "Sorry, something went wrong."
        })
        return

    ai_msg = result.get("ai message", "")

    st.session_state.threadMessages[threadID].append({
        "role": "ai",
        "content": ai_msg
    })


def loginView():
    st.title("💬 Chat Login")

    username = st.text_input("Enter Username")

    if st.button("Login"):
        if username.strip() == "":
            st.error("Username required")
            return

        login(username)
        st.rerun()


def sidebarView():
    st.sidebar.title("Chats")

    if st.sidebar.button("➕ New Chat"):
        newThreadID = str(uuid4())
        st.session_state.threads.append(newThreadID)
        st.session_state.threadMessages[newThreadID] = []
        st.session_state.activeThreadId = newThreadID
        st.rerun()

    for threadID in st.session_state.threads:
        if st.sidebar.button(threadID, key=f"thread_{threadID}"):
            st.session_state.activeThreadId = threadID
            st.rerun()


def chatView():
    sidebarView()
    ensure_thread_exists()

    threadID = st.session_state.activeThreadId

    st.title("💬 Chatbot")

    messages = st.session_state.threadMessages.get(threadID, [])

    for message in messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["content"])

    userInput = st.chat_input("Type your message")

    if userInput:
        sendQuery(userInput)
        st.rerun()


if not st.session_state.loginState:
    loginView()
else:
    chatView()